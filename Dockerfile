FROM python:3.11

WORKDIR /root/app/bottle-caps-backend

COPY . .
RUN pip install -r  requirements.txt --no-cache-dir

EXPOSE 8080

CMD ["fastapi", "run", "app/main.py", "--port", "8080"]