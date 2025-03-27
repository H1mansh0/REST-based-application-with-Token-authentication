from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

class Book(BaseModel):
    id: int = None
    title: str
    author: str

secret_database = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    {"id": 2, "title": "1984", "author": "George Orwell"},
    {"id": 3, "title": "To Kill a Mockingbird", "author": "Harper Lee"}
]

COMMUNICATING_TOKEN = os.getenv("TOKEN_FOR_COMMUNICATION")

def check_authorization(authorization):
    if authorization != f"Bearer {COMMUNICATING_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/")
def get_description():
    return {
        "description": "This is the database service, which give user ability to communicate with database. You can perform writing operation on endpoint /write. You can perform reading operation on endpoint /read."
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/read")
def get_data_from_db(authorization: str = Header(None)):
    check_authorization(authorization)

    return secret_database

@app.post("/write", status_code=201)
def write_data_to_db(book: Book, authorization: str = Header(None)):
    check_authorization(authorization)

    if not all([book.title, book.author]):
        raise HTTPException(
            status_code=400,
            detail="All fields must be provided"
        )

    book_id = max(secret_database, key=lambda x: x['id'], default=None)
    new_id = book_id['id'] + 1 if book_id else 1

    new_book = book.model_dump()
    new_book['id'] = new_id

    secret_database.append(new_book)

    return new_book