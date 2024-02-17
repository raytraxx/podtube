FROM python:3.12.1-slim-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER www-data

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app"]
