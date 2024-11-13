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


@asynccontextmanager
async def lifespan(app: FastAPI):
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=os.environ["OPENAI_API_KEY"],
    )
    encoder_model = SentenceTransformer("deepvk/USER-bge-m3", device=0 if is_available() else -1)
    app.state.answer_bot = AnswerBot(llm, Retriever(encoder_model=encoder_model))
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def ping():
    return {"content": "Hello, friend!"}


@app.post("/commit_question")
async def commit_question(request: Request, question: QuestionBody):
    bot = request.app.state.answer_bot
    data = BotAnswer(answer=bot.invoke(query=question.question, session_id=question.session_id))
    return JSONResponse(content=data.model_dump())
