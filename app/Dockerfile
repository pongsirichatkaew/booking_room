FROM python:3.7.2

ADD . /code
WORKDIR /code
ADD requirements.txt /code
RUN pip install -r requirements.txt
EXPOSE 7777
CMD ["python","app.py"]
