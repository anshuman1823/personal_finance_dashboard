#base image
FROM python:3.9

#work dir
WORKDIR /app

#copy
COPY . /app

#run
RUN pip install -r requirements.txt

#port
EXPOSE 8888

# command

CMD ["python", "./dashboard.py"]