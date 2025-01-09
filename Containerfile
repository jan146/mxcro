FROM python:3.12-alpine

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 5000
# CMD ["python", "-m", "user_info.src.api.v1.api"]

