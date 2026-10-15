FROM python:3.13.7-slim
WORKDIR /workspace
COPY services/api/requirements.lock /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY services/api ./services/api
COPY scripts ./scripts
ENV PYTHONPATH=/workspace/services/api
EXPOSE 8000
CMD ["sh", "-c", "alembic -c services/api/alembic.ini upgrade head && python scripts/seed.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
