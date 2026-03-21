FROM python:3.12-alpine

WORKDIR /loadgen
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY loadgen.py .

CMD ["python", "-u", "loadgen.py"]
