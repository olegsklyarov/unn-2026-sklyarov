FROM python:3.14-alpine
WORKDIR /app
COPY bot/ bot/
COPY migrations/ migrations/
ENV DATABASE_PATH=/data/database.sqlite
ENV MIGRATIONS_DIR=/app/migrations
VOLUME /data
CMD ["python", "-u", "-m", "bot"]
