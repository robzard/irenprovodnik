FROM python:3.10-buster

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

ENV PYTHONPATH="/common:/app:${PYTHONPATH}"

CMD ["bash", "-c", "export PYTHONPATH='/common:/app' && python tasks.py"]
