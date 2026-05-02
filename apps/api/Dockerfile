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
RUN pip install --no-cache-dir -e "."

# Copy app source
COPY . .

# Railway injects $PORT; default 8000 for local
ENV PORT=8000

CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
