import streamlit as st

from utils import commit_question

st.set_page_config(layout="wide")


if __name__ == "__main__":
    st.sidebar.title("Answer Bot")
    st.sidebar.write("This bot purpose is to answer questions about scientists and their achievements")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Привет, я дружелюбный бот, задавайте мне вопросы!"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Не стесняйтесь задавать вопросы"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = commit_question(prompt)["answer"]
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})