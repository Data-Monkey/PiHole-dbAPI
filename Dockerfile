FROM python:3

WORKDIR /usr/src/PiHoleDBAPI/

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

RUN mkdir /etc/pihole

CMD ["python", "./app/main.py"]