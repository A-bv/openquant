# Hugging Face Space — build and serve the OpenQuant FastAPI engine.
#
# The Space holds only this Dockerfile and a README; it clones the monorepo at
# build time, installs the engine package, and serves it. To ship a new version,
# hit "Factory rebuild" on the Space — it pulls the latest main. No secrets,
# no payment method.
FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN git clone --depth 1 https://github.com/A-bv/openquant.git . \
    && pip install --no-cache-dir "./engine[api]"

WORKDIR /app/engine

# The container runs as a non-root user on HF; make the fetch cache writable.
RUN mkdir -p /app/engine/data/cache && chmod -R 777 /app/engine/data

EXPOSE 7860
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
