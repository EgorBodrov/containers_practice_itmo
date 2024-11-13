from pathlib import Path
import requests
import os

from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.resolve() / ".env")


BASE_URL = os.environ["CONTAINER_URL"] if "CONTAINER_URL" in os.environ else "http://localhost:4242"


class QuestionBody(BaseModel):
    question: str = Field(description="Your question to bot")
    session_id: str = Field(description="session id of user")


def commit_question(question: str):
    body = QuestionBody(question=question, session_id="session_user_1")
    url = f"{BASE_URL}/commit_question"

    answer = requests.post(url, json=body.model_dump())
    return answer.json()
