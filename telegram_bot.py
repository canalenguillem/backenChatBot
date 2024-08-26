from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from chatgpt import chat_gpt_response
from text_to_speech import convert_text_to_speech
from decouple import config
from context import reset_context,load_context,update_context


# Cargar el token del bot desde el archivo .env
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hola! Envíame un mensaje de texto y te responderé con un audio.')

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    reset_context(initial_context=user_message)
    await update.message.reply_text('Contexto reseteado empecemos de nuevo')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Obtener el mensaje de texto enviado por el usuario
    user_message = update.message.text
    msg={
            "role": "user",
            "content": user_message
        }
    update_context(msg)
    # Generar respuesta usando chatgpt.py
    respuesta = chat_gpt_response()
    msg={
            "role": "assistant",
            "content": respuesta
        }
    update_context(msg)
    
    # Convertir la respuesta a audio usando text_to_speech.py
    audio_content = convert_text_to_speech(respuesta)

    # Guardar el audio en un archivo
    audio_file = "respuesta.mp3"
    with open(audio_file, 'wb') as f:
        f.write(audio_content)

    # Enviar el archivo de audio al usuario
    await update.message.reply_voice(voice=open(audio_file, 'rb'))

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Comandos
    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("reset",reset))

    # Mensajes
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Iniciar el bot
    application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
