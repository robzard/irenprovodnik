import asyncio
import os
import re

# from gigachat import GigaChat
from langchain.chat_models import GigaChat
from chromadb.config import Settings
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain.prompts import load_prompt

from config_data.config import load_config


class GPT:

    def __init__(self):
        self.text_system = None
        self.documents = None
        self.embeddings = None
        self.loader = None
        self.db = None
        self.llm = None
        self.history = []
        self.max_len_history = 10
        # self.text_system = "ты должен найти ответы на вопрос, если ты нашёл несколько ответов, то совмести их не изменяя текст. ищи ответ с наиболее подходящим вопросом. если ты не знаешь ответ на вопрос скажи 'Вызываю оператора'. ты должен сказать полный ответ, который нашёл, не изменяй текст и не добавляй никакого текста от себя."
        self.text_system = "необходимо найти по вопросу от пользователя самые подходящий вопросы и написать все ответы. ответ не изменяй, он должен быть в исходном виде, это очень важно. ты должен написать только найденные ответы.если ты не знаешь ответ или не нашёл все ответы на вопрос скажи 'Вызываю оператора'."
        f"Вопрос: "

    async def init(self):
        config = load_config()

        self.llm = GigaChat(credentials=config.tg_bot.gigachat_token, verify_ssl_certs=False)
        self.llm.max_tokens = 500
        self.llm.temperature = 1

        self.loader = TextLoader("text.txt")
        self.documents = self.loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=500,
        )
        self.documents = text_splitter.split_documents(self.documents)
        print(f"Total documents: {len(self.documents)}")

        self.embeddings = GigaChatEmbeddings(
            credentials=os.getenv("GIGACHAT_TOKEN"), verify_ssl_certs=False
        )

        self.db = Chroma.from_documents(
            self.documents,
            self.embeddings,
            client_settings=Settings(anonymized_telemetry=False),
        )

    async def ask_gigachat(self, user_question: str, history: list) -> str and list:

        # Получение наиболее релевантных документов
        docs = self.db.similarity_search(user_question, k=100)

        # Преобразование выбранных документов в текст для запроса
        relevant_docs_text = " ".join([doc.page_content for doc in docs])

        # Формирование итогового запроса, включающего в себя исходный запрос пользователя и текст релевантных документов
        optimized_query = self.text_system + user_question

        qa_chain = RetrievalQA.from_chain_type(self.llm, retriever=self.db.as_retriever())
        res = qa_chain({"query": optimized_query})
        answer = re.sub(r"Ответ №\d+:\s*", "", res['result'])
        return answer

    def history_append(self, msg: str | list):
        if isinstance(msg, list):
            self.history += msg
        else:
            if len(self.history) == self.max_len_history:
                self.history.pop(0)
            self.history.append(msg)


async def main():
    gpt = GPT()
    await gpt.init()
    while True:
        user_input = input("Введите сообщение: ")
        if not user_input:
            break
        print(await gpt.ask_gigachat(user_input, []))


asyncio.run(main())
