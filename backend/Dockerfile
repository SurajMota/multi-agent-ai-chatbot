# -------- Base Image --------
FROM python:3.11-slim

# -------- System Settings --------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -------- Working Directory --------
WORKDIR /app

# -------- Install System Dependencies --------
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------- Install Python Dependencies --------
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# -------- Copy Project --------
COPY . .

# -------- Expose Port --------
EXPOSE 8000

# -------- Start Server --------
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
