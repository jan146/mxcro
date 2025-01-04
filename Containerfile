FROM python:3.12-alpine

RUN apk update && \
    apk add git

WORKDIR /app
RUN git clone "https://github.com/jan146/mxcro.git"
WORKDIR /app/mxcro
RUN pip install -r requirements.txt

EXPOSE 5000
# CMD ["python", "-m", "user_info.src.api.v1.api"]

