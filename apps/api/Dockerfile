FROM python:3.12-slim

WORKDIR /app

# System deps: PostGIS client libs + GDAL + build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    g++ \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL env so geoalchemy2/shapely find it
ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install Python deps first (layer cache)
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir psycopg2-binary
RUN pip install --no-cache-dir -e "."

# Cache-bust: Render's layer cache can serve a stale COPY that misses newly
# added files (e.g. alembic migrations), causing an "unknown revision" boot
# crash. Bump this value to force a fresh source copy on the next build.
ARG SOURCE_CACHEBUST=20260720-1
RUN echo "source cachebust: ${SOURCE_CACHEBUST}"

# Copy app source
COPY . .

# Railway injects $PORT; default 8000 for local
ENV PORT=8000

# Run migrations, but never let a migration hiccup crash-loop the service:
# start uvicorn regardless (the schema is applied idempotently).
CMD alembic upgrade head || echo "WARNING: alembic upgrade head failed; starting API anyway"; uvicorn app.main:app --host 0.0.0.0 --port $PORT
