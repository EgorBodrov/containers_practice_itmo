from typing import List

from langchain_core.output_parsers import BaseOutputParser, StrOutputParser
from langchain_core.messages import BaseMessage, FunctionMessage
from langchain_core.language_models import BaseChatModel

from agent.nodes._base import BaseNode, AgentState, ConversationType
from agent.data import Retriever


CONVERSATION_NODE_PROMPT_TEMPLATE = """
## System
Ты помощник в ответе на вопросы пользователя про ученых и их достижения.

## Твоя задача
Тебе на вход приходит вопрос пользователя история диалога HISTORY.
Твоя задача понять по истории диалога, поменял ли пользователь тему или нет.

## Формат данных
HISTORY - строка, где общается пользователь (user) и другой ассистент (assistant)
Выведи число 1 - если пользователь поменял тему, 0 - если не поменял тему.
Ответом обязательно должно быть только число 1 или 0, не добавляй никаких символов, рассуждений и т.д.

## Пример 1
HISTORY:
user: Привет, в каком году Эйнштейн получил Нобелевскую премию?
assistant: В 1921 году.
user: А за что?
Твой ответ:
0

## Пример 2
HISTORY:
user: Как автор теории относительности?
assistant: Альберт Эйнштейн
user: А кто создал таблицу химических элементов?
Твой ответ:
1

HISTORY:
{history}
Твой ответ:
"""


class ConversationNode(BaseNode):
    def __init__(
        self,
        llm: BaseChatModel,
        prompt: str = CONVERSATION_NODE_PROMPT_TEMPLATE,
        output_parser: BaseOutputParser = StrOutputParser(),
    ) -> None:
        super().__init__(llm, prompt, output_parser)

    def _invoke(self, input: AgentState) -> AgentState:
        messages = input.messages
        
        if len(messages) > 1:
            roles = ("user", "assistant")
            history = "\n".join([f"{roles[ind % 2]}: {x.content}" for ind, x in enumerate(messages[-3:])
                                if not isinstance(x, FunctionMessage)])
            answer = self._chain.invoke({"history": history})
        else:
            answer = "1"
        
        assert len(answer) == 1
        answer = int(answer)
        new_status = "new" if answer == 1 else "old"

        print("CONVERSATION NODE")
        print(f"NEW STATUS: {new_status}")

        return {"status": new_status, "messages": messages}
