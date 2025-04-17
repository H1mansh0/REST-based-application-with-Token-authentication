FROM python:3.11.4

WORKDIR /app
COPY ./app .

RUN pip install --no-cache-dir -r requirements.txt

ENV API_KEY=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
ENV CLIENT_TOKEN=supersecretclienttoken
ENV TOKEN_FOR_COMMUNICATION=tokenforinternalusage
ENV DB_URL=http://127.0.0.1:9000
ENV BUSINESS_URL=http://127.0.0.1:8001

EXPOSE 8000

CMD [ "bash", "start_script.bash" ]

