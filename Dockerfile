FROM python:slim

WORKDIR /app

# Setup dependencies
RUN pip install --upgrade pip
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["gunicorn", "--bind", ":5050", "app:app", "--workers", "3"]
