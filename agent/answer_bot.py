from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from agent.nodes import ConversationNode, RAGNode, AgentState
from agent.data import Retriever


class AnswerBot:
    def __init__(self, llm: BaseChatModel, retriever: Retriever) -> None:
        self.llm = llm
        self.retriever = retriever
        self.memory = {}

        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        conversation_node = ConversationNode(llm=self.llm)
        rag_node = RAGNode(llm=self.llm, retriever=self.retriever)

        workflow.add_node("conversation", conversation_node.invoke)
        workflow.add_node("rag", rag_node.invoke)

        workflow.add_edge(START, "conversation")
        workflow.add_edge("conversation", "rag")
        workflow.add_edge("rag", END)

        return workflow.compile()

    def invoke(self, query: str, session_id: str) -> str:
        if session_id not in self.memory:
            self.memory[session_id] = []

        messages = self.memory[session_id]
        messages.append(HumanMessage(content=query))

        answer = self.graph.invoke({
            "status": "new",
            "messages": messages
        })
        self.memory[session_id] = answer["messages"]
        
        return answer["messages"][-1].content


if __name__ == "__main__":
    from pathlib import Path
    import os

    from langchain_openai import ChatOpenAI
    from sentence_transformers import SentenceTransformer
    from torch.cuda import is_available
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent.resolve() / ".env")


    llm = ChatOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL"),
        model="gpt-4o",
    )
    encoder_model = SentenceTransformer("deepvk/USER-bge-m3", device=0 if is_available() else -1)
    retriever = Retriever(encoder_model=encoder_model)
    bot = AnswerBot(llm, retriever)

    print(bot.invoke("Кто открыл периодический закон химических элементов?", "test_user"))
