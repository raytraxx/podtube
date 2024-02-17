FROM python:3.12.1-slim-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
USER www-data

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app", "-c", "gunicorn.conf.py"]
