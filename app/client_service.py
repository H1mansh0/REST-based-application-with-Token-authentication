from fastapi import FastAPI, HTTPException, Header
from dotenv import load_dotenv
import os
import requests
from pydantic import BaseModel

class Book(BaseModel):
    id: int = None
    title: str
    author: str

load_dotenv()

app = FastAPI()

APP_TOKEN = os.getenv("CLIENT_TOKEN")
COMMUNTICATING_TOKEN = os.getenv("TOKEN_FOR_COMMUNICATION")
DB_URL = os.getenv("DB_URL")
BUSINESS_URL = os.getenv("BUSINESS_URL")

def check_authorization(authorization):
    if authorization != f"Bearer {APP_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/")
def get_description():
    return {
        "description": "This is client service, the only service which can interact with external users. You can write new books to the database and read old books from it: use /books/write endpoint for writing and /books/read endpoint for reading. You can also get a recommendation based on your preferences about which book you might like: use /recommendation?preferences=value for receiving recommndation"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/books/read")
def read_database(authorization: str = Header(None)):
    check_authorization(authorization)
    
    health_status = requests.get(url=f"{DB_URL}/health")

    if health_status.json()["status"] == "ok":
        books = requests.get(url=f"{DB_URL}/read",
                             headers={"Authorization": f"Bearer {COMMUNTICATING_TOKEN}"})
        return books.json()
    else:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
@app.post("/books/write", status_code=201)
def write_database(book: Book, authorization: str = Header(None)):
    check_authorization(authorization)

    health_status = requests.get(url=f"{DB_URL}/health",)

    if health_status.json()["status"] == "ok":
        response = requests.post(f"{DB_URL}/write",
                                 json={"title": book.title, "author": book.author},
                                 headers={"Authorization": f"Bearer {COMMUNTICATING_TOKEN}"})

        if response.status_code == 201:
            return {"message": "Book successfully added", "book": response.json()}
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to add book")
    else:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
@app.get("/recommendation")
def get_recommendation(preferences, authorization: str = Header(None)):
    check_authorization(authorization)

    health_status = requests.get(url=f"{BUSINESS_URL}/health",)

    if health_status.json()["status"] == "ok":
        response = requests.get(f"{BUSINESS_URL}/recommendation?preferences={preferences}",
                                headers={"Authorization": f"Bearer {COMMUNTICATING_TOKEN}"})
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to get recomendation")
    else:
        raise HTTPException(status_code=503, detail="Service unavailable")