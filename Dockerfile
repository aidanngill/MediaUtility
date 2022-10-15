FROM python:bullseye

WORKDIR /app

RUN apt update -y && apt upgrade -y && apt install ffmpeg -y

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "-m", "src"]
