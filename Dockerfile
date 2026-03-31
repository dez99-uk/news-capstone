FROM python:3.11

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install mysqlclient

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --settings=news_project.docker_settings && python manage.py runserver 0.0.0.0:8000 --settings=news_project.docker_settings"]