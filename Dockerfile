FROM python:bullseye

WORKDIR /app

RUN apt update -y && apt upgrade -y && apt install ffmpeg -y

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "-m", "src"]
