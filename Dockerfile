FROM python:3.12.4

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get -y upgrade && \
    pip install -r requirements.txt

EXPOSE 8080

COPY app .

ENTRYPOINT ["streamlit", "run"]

CMD ["main.py", "--server.port", "8080"]
