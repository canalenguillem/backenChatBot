from decouple import config
import requests
# Cargar la clave API desde el archivo .env
ELEVENLABS_API_KEY = config('ELEVENLABS_API_KEY')




def convert_text_to_speech(message,voice_id="GU58mv1oQani2qjXfdf8",output_file="output.mp3"):
    body = {
    "text": message,
    "model_id":"eleven_turbo_v2_5", # use the turbo model for low latency
    "voice_settings": {
        "stability": 0,
        "similarity_boost": 0
        }
    }
    id_to_use=voice_id
    print(f"id to use {id_to_use}")
    headers = { "xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json", "accept": "audio/mpeg" }
    endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{id_to_use}"

    try:
        print("-------- enviando peticioón a eleven labs-----")
        response=requests.post(endpoint,json=body,headers=headers)

        # Guardar la respuesta de audio en un archivo
        with open(output_file, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        print(f"error convirtiendo texto a audio")

    if response.status_code==200:
        return response.content
    else:
        return
if __name__ == "__main__":
    convert_text_to_speech("hola me llamo guillem, y tu quien eres?")

