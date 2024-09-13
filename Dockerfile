FROM python:3.12.4-alpine3.20

ENV PORT=8000
ENV HOST=0.0.0.0

COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY src /app

WORKDIR /app
CMD ["python", "app.py"]
