FROM docker.io/python:3.11-alpine

COPY ./vib.py /vib.py

RUN pip3 install requests

ENTRYPOINT ["python3", "-u", "/vib.py"]

