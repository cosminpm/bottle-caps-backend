FROM python:3.12

WORKDIR /root/app/bottle-caps-backend

COPY . .
RUN pip install -r  requirements.txt --no-cache-dir

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]