from fastapi import FastAPI,File,UploadFile,HTTPException
from fastapi.responses import StreamingResponse

from context import reset_context,update_context,load_context
from chatgpt import chat_gpt_response,transcribe_audio
from text_to_speech import convert_text_to_speech

app=FastAPI()

@app.get("/")
def read_root():
    return {"Hola":"Alumno"}

@app.post("/reset/")
def reset(my_context="Quiero que hables y me contestes como un pirata del caribe, usar un máximo de 30 palabras y termina siempre con una pregunta"):
    reset_context(my_context)
    return {"message":"reseted context"}


@app.post("/send_message/")
async def send_message(message):
    respuesta=send_msg_to_chat(message)
    return {"response":respuesta}

def send_msg_to_chat(message):
    msg={
        "role":"user",
        "content":message
    }
    update_context(msg)
    respuesta=chat_gpt_response()
    msg={
        "role":"assistant",
        "content":respuesta
    }
    update_context(msg)
    return respuesta

@app.post("/post-audio")
async def post_audio(file: UploadFile = File(...)):

    #guardar el fichero
    with open(file.filename,"wb") as buffer:
        buffer.write(file.file.read())
    audio_input = open(file.filename, "rb")
    message=transcribe_audio(audio_input)
    print("audio transcrito: ",message)
    respuesta=send_msg_to_chat(message)

    #convertir la respuesta a mp3
    audio_output=convert_text_to_speech(respuesta)
    if not audio_output:
        return HTTPException(status_code=400,detail="Failed to convert text to speech")
    
    #tenemos el mp3 en audio output

    def iterfile():
        yield audio_output

    return StreamingResponse(iterfile(),media_type="application/octet-stream")        

    print(f"respuesta {respuesta}")
    return {"response":respuesta}





