FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY ./ ./

COPY entrypoint.sh .

RUN chmod 777 /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["echo"]