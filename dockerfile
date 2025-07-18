# Stage 1 - Build
FROM python:3.13-slim 
WORKDIR /app

COPY shakescript/backend/requirements.txt .

RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2 - Run
COPY shakescript/backend .

EXPOSE 80
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:80"]
