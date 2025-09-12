FROM public.ecr.aws/docker/library/python:3.12-slim
WORKDIR /app

# 依存
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# アプリ本体
COPY app.py /app/app.py

# Streamlit を 0.0.0.0:8080 で公開（ECS/ALB想定）
EXPOSE 8080

CMD ["streamlit","run","/app/app.py","--server.port","8080","--server.address","0.0.0.0"]
