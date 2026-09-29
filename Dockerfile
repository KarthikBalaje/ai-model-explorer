FROM python:3.10-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --prefix=/install \
    -r requirements.txt


FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=builder /install /usr/local

RUN python -m pip uninstall -y setuptools wheel \
    && rm -rf /root/.cache/pip

COPY app.py .
COPY templates ./templates
COPY static ./static

EXPOSE 5000

CMD ["python", "app.py"]