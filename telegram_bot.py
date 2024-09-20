from telegram import Update, Bot,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes,CallbackQueryHandler
from chatgpt import chat_gpt_response,transcribe_audio
from text_to_speech import convert_text_to_speech
from decouple import config
from context import reset_context,load_context,update_context
import json

# Cargar el token del bot desde el archivo .env
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')

# Cargar las voces desde el archivo JSON
with open('voices.json', 'r') as file:
    voices_data = json.load(file)
    available_voices = voices_data['voices']

# Diccionario para almacenar la selección de voz por usuario
user_voice_selection = {}

# ID de voz por defecto
DEFAULT_VOICE_ID = "GU58mv1oQani2qjXfdf8"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("funcion start")
    msg="Hola! Envíame un mensaje de texto y te responderé con un audio."
    await update.message.reply_text(msg)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #crear un nuevo contexto
    user_message=update.message.text
    print(f"user_message {user_message}")
    new_context=user_message.replace('/reset','').strip()
    if new_context:
        reset_context(initial_context=new_context)
        await update.message.reply_text('Contexto reseteado empecemos de nuevo')
    else:
        await update.message.reply_text('Por favor proporciona un contexto')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update.message.voice)
    user_id=update.message.from_user.id
     # Asignar la voz por defecto si el usuario no tiene una voz seleccionada
    if user_id not in user_voice_selection:
        user_voice_selection[user_id] = DEFAULT_VOICE_ID
    print(f"default voice {user_voice_selection}")


    if update.message.text:
        print("text message")
        user_message=update.message.text
    elif update.message.voice:
        # Manejo de mensajes de voz
        print("voice message")
        file = await update.message.voice.get_file()
        audio_file_path = "input.ogg"
        await file.download_to_drive(audio_file_path)


         # Transcribir el audio
        with open(audio_file_path, "rb") as audio_file:
            transcribed_text = transcribe_audio(audio_file)
        user_message=transcribed_text
    #user_message contiene lo que nos envia el usuario en formato texto
    print(user_message)

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
    audio_content = convert_text_to_speech(respuesta,voice_id=user_voice_selection[user_id])

    # Guardar el audio en un archivo
    audio_file = "respuesta.mp3"
    with open(audio_file, 'wb') as f:
        f.write(audio_content)

    await update.message.reply_voice(voice=open(audio_file,'rb'))


async def voices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard= [[InlineKeyboardButton(voice["name"], callback_data=voice["id"])] for voice in available_voices]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Selecciona una voz:', reply_markup=reply_markup)


async def select_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query=update.callback_query
    print(f"query {query.data}")
    selected_voice_id=query.data
    user_id=query.from_user.id
    user_voice_selection[user_id]=selected_voice_id

    await query.answer()
    await query.edit_message_text(text=f"Voz seleccionada: {selected_voice_id}")



    


def main()-> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset",reset))
    application.add_handler(CommandHandler("voices", voices))


     # Mensajes
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_message))  # Manejo de mensajes de voz

    # Manejador de la selección de voz
    application.add_handler(CallbackQueryHandler(select_voice))


    # Iniciar el bot
    application.run_polling()




if __name__ == "__main__":
    import asyncio
    asyncio.run(main())