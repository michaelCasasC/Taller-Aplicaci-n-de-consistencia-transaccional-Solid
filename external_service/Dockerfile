FROM python:3.12-slim
WORKDIR /service
RUN pip install --no-cache-dir Flask==3.1.0
COPY server.py .
EXPOSE 5001
ENV PYTHONUNBUFFERED=1
CMD ["python","server.py"]
