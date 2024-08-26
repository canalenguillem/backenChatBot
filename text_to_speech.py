from decouple import config
import requests
# Cargar la clave API desde el archivo .env
ELEVENLABS_API_KEY = config('ELEVENLABS_API_KEY')




def convert_text_to_speech(message,output_file="output.mp3"):
    body = {
    "text": message,
    "model_id":"eleven_turbo_v2_5", # use the turbo model for low latency
    "voice_settings": {
        "stability": 0,
        "similarity_boost": 0
        }
    }
    voice_rachel="21m00Tcm4TlvDq8ikWAM"
    charlie_id="IKne3meq5aSn9XLyUdCD"
    enguillem="GU58mv1oQani2qjXfdf8"
    id_to_use=enguillem
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

