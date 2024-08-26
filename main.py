from fastapi import FastAPI,File,UploadFile,HTTPException
from fastapi.responses import StreamingResponse

from context import reset_context,update_context,load_context
from chatgpt import chat_gpt_response,transcribe_audio
from text_to_speech import convert_text_to_speech

from fastapi.middleware.cors import CORSMiddleware


app=FastAPI()

# CORS - Origins
origins = [
    "http://localhost:5173",
]

# CORS - Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hola":"Alumno"}

@app.post("/reset/")
def reset(my_context="Toma el papel de un profesor nativo en inglés, tienes una charla con un alumno al que tienes que responder y darle algunas recomandaciones de mejora, responde siempre en inglés y con una pregunta sobre el tema para seguir la conversación de forma fluída"):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



