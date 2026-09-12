# Használjunk egy könnyű súlyú Python imázst
FROM python:3.10-slim

# Munkamappa kijelölése a konténeren belül
WORKDIR /app

# Először csak a függőségeket másoljuk át (a gyorsabb cache-elés miatt)
COPY requirements.txt .

# Függőségek telepítése
RUN pip install --no-cache-dir -r requirements.txt

# Majd átmásoljuk a teljes programkódot és a log fájlt
COPY . .

# Alapértelmezett parancs, ami lefut, ha elindul a konténer
CMD ["python", "src/monitor.py"]