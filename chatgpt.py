from openai import OpenAI
from decouple import config
from context import reset_context,load_context,update_context

api_key=config('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def chat_gpt_response():
    context=load_context()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=context
    )
    return completion.choices[0].message.content

def transcribe_audio(audio_file):
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
        )
    return transcription.text


if __name__ == "__main__":
    contexto=input("Introduce el contexto: ")
    reset_context(initial_context=contexto)
    
    entrada=input("introduce un mensaje: ")
    while entrada!="exit":
        msg={
            "role": "user",
            "content": entrada
        }
        update_context(msg)
        respuesta=chat_gpt_response()

        msg={
            "role": "assistant",
            "content": respuesta
        }
        update_context(msg)
        print(f"respuesta: {respuesta}")
        entrada=input("introduce un mensaje: ")



