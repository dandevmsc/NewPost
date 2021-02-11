FROM python:3.9
WORKDIR /src
RUN python -m pip install pyyaml
RUN python -m pip install argh
RUN pip install watchdog
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "./newpost.py"]
