from pathlib import Path
import os

from sentence_transformers import SentenceTransformer
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from langchain_openai import ChatOpenAI
from fastapi import FastAPI, Request
from torch.cuda import is_available
from dotenv import load_dotenv

from models import QuestionBody, BotAnswer
from agent.data import Retriever
from agent import AnswerBot


load_dotenv(Path(__file__).parent.parent.resolve() / ".env")

DATA_PATH = Path(__file__).parent / "data"
RAW_DATA_PATH = Path(__file__).parent.parent / "agent" / "data" / "data_raw.txt"


@asynccontextmanager
async def lifespan(app: FastAPI):
    llm = ChatOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL"),
        model="gpt-4o",
    )
    encoder_model = SentenceTransformer("deepvk/USER-bge-m3", device="cuda" if is_available() else "cpu")
    url = os.environ.get("QDRANT_URL")
    retriever = Retriever(encoder_model=encoder_model, url=url)
    app.state.answer_bot = AnswerBot(llm, retriever=retriever)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def ping():
    return {"content": "Hello, friend!"}


@app.post("/commit_question")
async def commit_question(request: Request, question: QuestionBody):
    bot = request.app.state.answer_bot
    data = BotAnswer(answer=bot.invoke(query=question.question, session_id=question.session_id))

    with open(DATA_PATH / f"{question.session_id}_data", "w+") as file:
        file.write(f"{question.question}\n{data.answer}\n")

    return JSONResponse(content=data.model_dump())
