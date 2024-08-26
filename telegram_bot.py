from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from chatgpt import chat_gpt_response,transcribe_audio
from text_to_speech import convert_text_to_speech
from decouple import config
from context import reset_context,load_context,update_context
import os



# Cargar el token del bot desde el archivo .env
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hola! Envíame un mensaje de texto y te responderé con un audio.')

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    # Eliminar el comando '/reset' y cualquier espacio que lo siga
    new_context = user_message.replace('/reset', '').strip()

    if new_context:
        reset_context(initial_context=new_context)
        await update.message.reply_text('Contexto reseteado empecemos de nuevo')
    else:
        await update.message.reply_text('Por favor, proporciona un nuevo contexto después de /reset.')



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"voice {update.message.audio}")
    if update.message.text:
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
    elif update.message.voice:
        # Manejo de mensajes de voz
        file = await update.message.voice.get_file()
        audio_file_path = "input.ogg"
        await file.download_to_drive(audio_file_path)
        
        # Transcribir el audio
        with open(audio_file_path, "rb") as audio_file:
            transcribed_text = transcribe_audio(audio_file)
        
        # Eliminar el archivo de audio descargado
        os.remove(audio_file_path)
        
        # Continuar el flujo como si fuese un mensaje de texto
        msg = {
            "role": "user",
            "content": transcribed_text
        }
        update_context(msg)
        
        # Generar respuesta usando chat_gpt_response
        respuesta = chat_gpt_response()
        
        msg = {
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
    application.add_handler(MessageHandler(filters.VOICE, handle_message))  # Manejo de mensajes de voz


    # Iniciar el bot
    application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
