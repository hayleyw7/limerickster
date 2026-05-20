# Hugging Face Docker Space — https://huggingface.co/docs/hub/spaces-sdks-docker
FROM python:3.11-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user . /app

ENV PORT=7860
EXPOSE 7860

CMD gunicorn --bind 0.0.0.0:7860 --workers 1 --threads 4 app:app
