from abc import ABC, abstractmethod
from typing import List, Literal

from langchain_core.output_parsers import BaseOutputParser, StrOutputParser
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import BaseMessage
from pydantic import BaseModel


ConversationType = Literal["new", "old"]


class AgentState(BaseModel):
    status: ConversationType
    messages: List[BaseMessage]


class BaseNode(ABC):
    def __init__(
        self,
        llm: BaseChatModel,
        prompt: str,
        output_parser: BaseOutputParser = StrOutputParser(),
    ) -> None:
        self._chain = PromptTemplate.from_template(prompt) | llm | output_parser

    @abstractmethod
    def _invoke(self, input: AgentState):
        pass

    def invoke(self, input: AgentState):
        return self._invoke(input)
