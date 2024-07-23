import json

CONTEXT_FILE="context.json"

def load_context():
    try:
        with open(CONTEXT_FILE,"r",encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_context(context):
    with open(CONTEXT_FILE,"w",encoding="utf-8") as file:
        json.dump(context,file,ensure_ascii=False,indent=4)

def update_context(msg):
    context=load_context()
    context.append(msg)
    save_context(context)


def reset_context(initial_context="Eres el jefe de departamento de recursos humanos de una empresa de desarrollo web y vas a hacer una entrevista de trabajo para un candidato, usar un máximo de 40 palabras y usa un poco de humor sarcástico y acaba siempre con una pregunta para seguir con la entrevista"):
    context=[
        {"role":"system","content":initial_context}
    ]

    save_context(context)


if __name__ == "__main__":
    reset_context()
