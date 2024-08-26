from telegram import Update
from telegram.constants import ParseMode

from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes,CallbackQueryHandler
import requests
from decouple import config  # Importar config para manejar el token de manera segura
from scraping import scrapear_comunidad
from services import get_subastas_activas,numero_subastas_activas_todas_provincias
import re
from services import log_command_usage, register_or_update_user
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

TELEGRAM_TOKEN = config('TELEGRAM_BOT_TOKEN')  # Usar decouple para obtener el token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    register_or_update_user(user.id, user.username, user.first_name, user.last_name)
    log_command_usage(user.id, '/start')

    keyboard = [
        [InlineKeyboardButton("Ayuda", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    response_message = f"Hola {user.first_name}, bienvenido al bot! Para obtener más información sobre cómo usar el bot, presiona el botón de ayuda."
    await update.message.reply_text(response_message, reply_markup=reply_markup)



async def handle_menu_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Siempre responde las callback queries

    # Procesar el comando según el callback_data
    if query.data == 'help':
        help_message = (
            "Aquí están los comandos que puedes usar:\n\n"
            "/start - Reinicia la interacción con el bot y muestra este mensaje.\n"
            "/activas <prefijo postal> - Muestra las subastas activas para el prefijo postal especificado, ej. /activas 07.\n"
            "/actualiza <prefijo postal> - Actualiza la base de datos de subastas para el prefijo postal especificado, ej. /actualiza 07.\n"
            "/cuantas - Muestra la cantidad de subastas activas por provincia.\n"
            "\nSimplemente escribe el comando con el prefijo postal apropiado para obtener la información que necesitas."
        )
        await query.edit_message_text(text=help_message, parse_mode=ParseMode.MARKDOWN)




async def actualiza(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text('Por favor incluye un prefijo postal después del comando, ej. /activas 07')
        return
    prefijo_postal = context.args[0]
    user = update.effective_user
    log_command_usage(user.id, f'/actualiza {prefijo_postal}')

    print(f"scrapea {prefijo_postal} ")
    insertados=scrapear_comunidad(prefijo_postal)
    await update.message.reply_text(f"terminado nuevas subastas: {insertados}")

async def activas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message or update.callback_query.message  # Esto maneja ambos contextos
    user = update.effective_user

    # Si la función fue llamada por un CallbackQuery, es posible que no haya context.args.
    if context.args:
        prefijo_postal = context.args[0]
    elif update.callback_query:
        # Puedes decidir cómo manejar la falta de args aquí, por ejemplo, pidiendo al usuario que escriba el prefijo.
        await message.reply_text('Por favor incluye un prefijo postal después del comando, ej. /activas 07')
        return
    prefijo_postal = context.args[0]
    log_command_usage(user.id, f'/activas {prefijo_postal}')

    # Validación simple del prefijo postal para asegurarse de que es numérico
    if not re.match(r'^\d{2}$', prefijo_postal):
        await update.message.reply_text('El prefijo postal debe ser numérico de dos dígitos, ej. 07')
        return

    await update.message.reply_text(f"Buscando subastas activas para el prefijo postal: {prefijo_postal}... Esto puede tomar un momento.")
    
    try:
        subastas = get_subastas_activas(prefijo_postal)
    
        if subastas:
            mensajes = [
                f"*{subasta['identificador']}* - {subasta['tipo_subasta']}\n*Días restantes:* {subasta['dias_restantes']}\n*Valor:* {subasta['valor_subasta']}\n*Descripción:* {subasta['descripcion']}"
                for subasta in subastas
            ]
            mensaje_final = "\n\n".join(mensajes)
            
            if len(mensaje_final) > 4096:
                partes = [mensaje_final[i:i+4096] for i in range(0, len(mensaje_final), 4096)]
                for parte in partes:
                    await update.message.reply_text(parte, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(mensaje_final, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text('No se encontraron subastas activas para este prefijo postal.')
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text('Hubo un error al recuperar las subastas activas. Por favor, inténtalo de nuevo más tarde.')

async def cuantas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    subastas_info = numero_subastas_activas_todas_provincias()
    user = update.effective_user
    log_command_usage(user.id, f'/cuantas')
    if subastas_info:
        mensajes = [
            f"*{provincia} ({prefijo})* - {num_subastas} subastas activas"
            for provincia, prefijo, num_subastas in subastas_info
        ]
        mensaje_final = "\n".join(mensajes)
        
        # Comprobar si el mensaje es demasiado largo y dividirlo si es necesario
        if len(mensaje_final) > 4096:
            partes = [mensaje_final[i:i+4096] for i in range(0, len(mensaje_final), 4096)]
            for parte in partes:
                await update.message.reply_text(parte, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(mensaje_final, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text('No se encontraron subastas activas o hubo un error en la solicitud.')


def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_menu_actions))

    application.add_handler(CommandHandler("activas", activas))  # Asegura que los argumentos sean pasados a la función
    application.add_handler(CommandHandler("actualiza",actualiza))
    application.add_handler(CommandHandler("cuantas", cuantas))

    application.run_polling()

if __name__ == '__main__':
    main()
