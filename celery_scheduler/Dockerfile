FROM python:3.10-buster

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

ENV PYTHONPATH="/common:/app:${PYTHONPATH}"

CMD ["python", "tasks.py"]
