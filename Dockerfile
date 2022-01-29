FROM python:3.9.7-buster

WORKDIR /src
COPY ./src /src
COPY ./requirements.txt /src/requirements.txt
ENTRYPOINT ["/bin/sh", "-l", "-c"]

RUN unlink /etc/localtime
RUN ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime

RUN pip install --no-cache -r /src/requirements.txt

CMD ["python main.py"]