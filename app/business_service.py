from fastapi import FastAPI, HTTPException, Header
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()

app = FastAPI()

API_TOKEN =  os.getenv("API_KEY")
COMMUNICATING_TOKEN = os.getenv("TOKEN_FOR_COMMUNICATION")
DB_URL = "http://127.0.0.1:9000"

def check_authorization(authorization):
    if authorization != f"Bearer {COMMUNICATING_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
def get_all_books() -> list:
    health_status = requests.get(url=f"{DB_URL}/health")

    if health_status.json()["status"] == "ok":
        books = requests.get(url=f"{DB_URL}/read",
                            headers={"Authorization": f"Bearer {COMMUNICATING_TOKEN}"})

        return books.json()
    else:
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/")
def get_description():
    return {
        "description": "This is the database service, which give user ability to communicate with database. You can perform writing operation on endpoint /write. You can perform reading operation on endpoint /read."
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/recommendation")
def get_recommandation(preferences: str, authorization: str = Header(None)):
    check_authorization(authorization)

    books = get_all_books()

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": "qwen/qwen2.5-vl-72b-instruct:free",
            "messages":[
                {
                    "role": "system",
                    "content":
                    f"""
                    List of books: {books}

                    You are a book recommendation system. Given a list of books.
                    The user will send their preferences, and you will suggest a book that best matches those preferences by returning its id in the list.

                    Each book in the list will have the following format:
                    - Id: not use
                    - Title: The title of the book
                    - Author: The author of the book

                    You must provide a recommendation based on the user’s preferences.
                    The preferences include only natural language query.
                        Example: I like fiction.
                    Your task by title and author of book, get its description and recommend book using it.
                    Return only id of book in provided list.

                    Example:
                        Books List:
                        [
                            {{"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"}},
                            {{"id": 2, "title": "1984", "author": "George Orwell"}},
                            {{"id": 3, "title": "To Kill a Mockingbird", "author": "Harper Lee"}}
                        ]

                        User Preferences:
                        I like George Orwell

                        Expected answer:
                        2

                    Your task is to recommend the best book from the list based on given user preferences.
                    """
                },
                {
                    "role": "user", 
                    "content": f"User preferences: {preferences}"
                }
            ]
        })
    )

    suggestion = int(response.json()['choices'][0]['message']['content'])
    result = next((book for book in books if book["id"] == suggestion), None)

    return result

