# News Capstone Project

GitHub: https://github.com/dez99-uk/news-capstone

## Setup (venv)

git clone https://github.com/dez99-uk/news-capstone.git
cd news-capstone
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

## Docker

docker build -t news-capstone .
docker run -p 8000:8000 news-capstone
