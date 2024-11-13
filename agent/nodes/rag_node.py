from typing import List

from langchain_core.messages import BaseMessage, FunctionMessage, AIMessage
from langchain_core.output_parsers import BaseOutputParser, StrOutputParser
from langchain_core.language_models import BaseChatModel

from agent.nodes._base import BaseNode, AgentState, ConversationType
from agent.data import Retriever


RAG_NODE_PROMPT_TEMPLATE = """
## System
Ты помощник в ответе на вопросы пользователя про ученых и их достижения.

## Твоя задача
Тебе на вход приходит вопрос пользователя QUESTION, собранная информация INFO.
Твоя задача ответить на вопрос QUESTION информацией из INFO максимально кратко и четко.
Не добавляй дополнительных деталей, которые не спрашивались в QUESTION.

## Требования
1. Нельзя придумывать информацию, бери данные только из INFO.
2. Если такой информации нет в INFO, то ответь честно что не знаешь ответа.

## Формат данных
QUESTION - строка
INFO - список абзацев релевантных к вопросу пользователя в виде строки.

## Пример
QUESTION:
В каком году Эйнштейн получил нобелевскую премию?
INFO:
1. Альберт Эйнштейн — физик немецкого происхождения. В 1921 ему присудили Нобелевскую премию за открытие закона фотоэлектрического эффекта.
2. Александр Сергеевич Пушкин - русский поэт и классик.
Твой ответ:
Альберт Эйнштейн получил Нобелевскую премию в 1921 году.

QUESTIONS:
{question}
INFO:
{info}
Твой ответ:
"""


class RAGNode(BaseNode):
    def __init__(
        self,
        llm: BaseChatModel,
        retriever: Retriever,
        prompt: str = RAG_NODE_PROMPT_TEMPLATE,
        output_parser: BaseOutputParser = StrOutputParser(),
    ) -> None:
        super().__init__(llm, prompt, output_parser)
        self._retriever = retriever

    def _get_info(self, messages: List[BaseMessage]):
        functional_messages = [x for x in messages if isinstance(x, FunctionMessage)
                               and x.name == "RAG"]
        return functional_messages[-1].content

    def _process_info(self, info: List) -> str:
        results = [f"{id+1}.{x.payload['text']}" for id, x in enumerate(info)]
        return "\n".join(results)

    def _invoke(self, input: AgentState) -> AgentState:
        status = input.status
        messages = input.messages
        question = messages[-1].content

        if status == "new":
            info = self._retriever.search(
                query=question,
                collection_name="scientists",
                topk=3
            )
            messages.append(FunctionMessage(name="RAG", content=self._process_info(info)))
        else:
            info = self._get_info(messages=messages)

        answer = self._chain.invoke({
            "question": question,
            "info": info,
        })
        messages.append(AIMessage(content=answer))

        print("RAG_NODE")
        print(info)

        return {"status": status, "messages": messages}
