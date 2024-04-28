from gigachat import GigaChat
from langchain_core.messages import BaseMessage

from gpt.texts import full_text
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.chat_models.gigachat import GigaChat

import os

# text1 = "Твоя роль - менеджер поддержки, который отвечает на вопросы пользователя. Отвечай чётко, коротко и передавай пользователю главную суть. Если ты не знаешь ответ на вопрос или его никакой информации нет в указанном тексте, то отвечай 'Вызов оператора'. Ищи в тексте все взаимосвязи и пиши все ньюансы по вопросу который я буду задавать. Отвечай по этому тексту:" + full_text
text1 = ("Ты менеджер и отвечаешь на вопросы только по тексту. Если ты не знаешь ответ на вопрос или его никакой информации нет в указанном тексте, то отвечай 'Вызов оператора'. "
         "Ты должен находить самый подходящий ответ на вопрос и писать его без изменений. Делай перенос строки где это необходимо, чтобы текст не был сплошной. Всегда пиши полный ответ. Не добавляй от себя ничего"
         "Отвечай по этому тексту:") + full_text


class GPT:

    def __init__(self):
        self.history = []
        self.max_len = 10

    async def ask_gpt(self, user_question: str, history: list) -> str and list:
        gigachat_token = os.getenv("GIGACHAT_TOKEN")
        chat = GigaChat(credentials=gigachat_token, verify_ssl_certs=False, scope="GIGACHAT_API_PERS", timeout=10)
        chat.max_tokens = 300
        chat.temperature = 1
        if not history:
            self.history_append([
                SystemMessage(content=text1),
                HumanMessage(content='Ответь на вопрос: У вас есть тариф без обратной связи'),
                AIMessage(
                    content='В нашей школе все тарифы только с обратной связью. \nКураторы проверяют ваши практические задания и дают подробную обратную связь, направляют вас. \nОбучение без обратной связи мы считаем не эффективным, а для нас важно, чтобы вы получили результат.'),
                HumanMessage(content='Ответь на вопрос: я хочу выполнять задания только онлайн'),
                AIMessage(content='Есть задания, которые нужно выполнять только офлайн, так вы отработаете теорию на практике и научитесь ориентироваться в ТЦ.\nВажно научиться работать с вещами и с клиентами офлайн.'),
                HumanMessage(content='Ответь на вопрос: хочу шопинг с Татьяной'),
                AIMessage(content='Вызов оператора.'),
                HumanMessage(content='Ответь на вопрос: сколько стоит реклама у Татьяны?'),
                AIMessage(content='Вызов оператора.'),
                HumanMessage(content='Ответь на вопрос: мы хотим с вами сотрудничать?'),
                AIMessage(content='Вызов оператора.'),
            ])

        self.history_append(HumanMessage(content=f"Ответь на вопрос: '{user_question}'  "))
        res: BaseMessage = chat(history)
        self.history_append(res)
        return res.content, history

    def history_append(self, msg: BaseMessage | list):
        if isinstance(msg, list):
            self.history += msg
        else:
            if len(self.history) == self.max_len:
                self.history.pop(0)
            self.history.append(msg)


'В этом потоке не будет тарифа с обратной связью лично от Татьяны, только с обратной связью от куратора, но все уроки проводит Татьяна и приглашенные спикеры. Также, Татьяна в курсе «Профессия-стилист» проводит прямые эфиры в закрытом аккаунте школы, где приводит примеры из своей практики и вы сможете задать ей свои вопросы.'
'В ближайшие полгода vip-группы не будет, следите за новостями в телеграм-канале школы.'
'В курсе «Стиль для себя» тариф только с обратной связью от куратора.'
