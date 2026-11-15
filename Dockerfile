FROM python:3.14-alpine
WORKDIR /app
COPY bot.py .
CMD ["python", "-u", "bot.py"]
