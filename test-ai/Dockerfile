FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y wget git && \
    pip install --upgrade pip setuptools wheel gdown

RUN mkdir -p .models

RUN pip install lap==0.4.0
RUN pip install -r requirements.txt

RUN wget -O .models/yolov8l-face.pt https://github.com/akanametov/yolov8-face/releases/download/v0.0.0/yolov8l-face.pt && \
    wget -O .models/yolov8l.pt https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8l.pt && \
    wget -O .models/yolov8n.pt https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt && \
    gdown 1J-PDWDAkYCdT8T2Nxn3Q_-iOHH_t-9YP -O .models/pretrain_TalkSet.model

CMD ["python", "main.py"]