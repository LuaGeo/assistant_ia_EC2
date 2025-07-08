from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
import uvicorn

# Charger les variables d'environnement
load_dotenv()

app = FastAPI(
    title="Assistant IA",
    description="API pour interroger un LLM via LangChain",
    version="1.0.0"
)

# Modèle pour la requête
class QuestionRequest(BaseModel):
    question: str
    system_prompt: str = "Tu es un assistant IA utile et bienveillant."

# Modèle pour la réponse
class QuestionResponse(BaseModel):
    answer: str
    question: str

# Initialiser le modèle LangChain
def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY non trouvée dans les variables d'environnement")
    
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        openai_api_key=api_key
    )

@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur votre Assistant IA !",
        "endpoints": {
            "/ask": "POST - Poser une question au LLM",
            "/health": "GET - Vérifier l'état du service",
            "/docs": "GET - Documentation interactive"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Assistant IA API"}

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    try:
        # Initialiser le LLM
        llm = get_llm()
        
        # Créer les messages
        messages = [
            SystemMessage(content=request.system_prompt),
            HumanMessage(content=request.question)
        ]
        
        # Obtenir la réponse
        response = llm.invoke(messages)
        
        return QuestionResponse(
            answer=response.content,
            question=request.question
        )
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Erreur de configuration: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")

@app.get("/examples")
async def get_examples():
    return {
        "examples": [
            {
                "question": "Explique-moi ce qu'est le machine learning",
                "system_prompt": "Tu es un expert en IA qui explique simplement."
            },
            {
                "question": "Donne-moi 3 conseils pour être plus productif",
                "system_prompt": "Tu es un coach en productivité."
            },
            {
                "question": "Écris un petit poème sur la programmation",
                "system_prompt": "Tu es un poète qui aime la technologie."
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )