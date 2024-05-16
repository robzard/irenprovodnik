FROM python:3.10-slim
WORKDIR /bot

# Установите зависимости
COPY requirements.txt .

RUN apt-get update && apt-get install -y libpq-dev
RUN pip install --upgrade pip && pip install -r requirements.txt

# Скопируйте исходный код бота в контейнер
COPY . .

ENV PYTHONPATH="/common:${PYTHONPATH}"

CMD ["python", "bot.py"]
