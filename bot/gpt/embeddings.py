import os

# ТОЧНО ЛУШЧЕ ВСЕХ ЧЕМ ВЫШЕ - взял тут https://habr.com/ru/companies/sberdevices/articles/794773/
# Нужно доработать, взять пример сверху и сделать сохранение базы, чтобы не загружал каждый раз при запуске

# from langchain_community.llms.gigachat import GigaChat
from gigachat import GigaChat
# from langchain.chat_models.gigachat import GigaChat
from langchain.document_loaders import TextLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)
from langchain.chains import RetrievalQA
from chromadb.config import Settings
from langchain.vectorstores import Chroma

from langchain_community.embeddings.gigachat import GigaChatEmbeddings

llm = GigaChat(credentials=os.getenv("GIGACHAT_TOKEN"), verify_ssl_certs=False)

loader = TextLoader("text.txt")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=500,
)
documents = text_splitter.split_documents(documents)
print(f"Total documents: {len(documents)}")

embeddings = GigaChatEmbeddings(
    credentials=os.getenv("GIGACHAT_TOKEN"), verify_ssl_certs=False
)

db = Chroma.from_documents(
    documents,
    embeddings,
    client_settings=Settings(anonymized_telemetry=False),
)

text_system = "ты должен найти ответ на вопрос. если ты не знаешь ответ на вопрос скажи 'Вызываю оператора'. ты должен сказать полный ответ, который нашёл, без сокращений."
f"Вопрос: "

while True:
    user_input = input("Введите сообщение: ")
    if not user_input:
        break

    # Получение наиболее релевантных документов
    docs = db.similarity_search(user_input, k=10)

    # Преобразование выбранных документов в текст для запроса
    relevant_docs_text = " ".join([doc.page_content for doc in docs])

    # Формирование итогового запроса, включающего в себя исходный запрос пользователя и текст релевантных документов
    optimized_query = text_system + user_input

    qa_chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())
    res = qa_chain({"query": optimized_query})
    print(res['result'])
##
