FROM python

WORKDIR /app

COPY .env .
COPY requirements.txt .
COPY entrypoint.sh .
COPY /social_network_backend .

RUN pip install -r requirements.txt

CMD [ "bash", "entrypoint.sh" ]