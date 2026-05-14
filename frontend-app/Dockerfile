FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY todolist.py .
COPY templates/index.html templates/index.html

EXPOSE 5000

CMD ["python", "-u", "todolist.py"]