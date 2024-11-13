from pydantic import BaseModel, Field


class QuestionBody(BaseModel):
    question: str = Field(description="Your question to bot")
    session_id: str = Field(description="session id of user")


class BotAnswer(BaseModel):
    answer: str = Field(description="Answer bot response")
