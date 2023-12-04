#Python 
FROM python:3.8

#Set the working directory to /src 
WORKDIR /app

#Copy local code  to the container
COPY . /app

#Install any needed dependencies
#RUN pip install --no-cache-dir -r requirements.txt

#Command to run on container start
CMD [ "python", "aws_handler.py", "lambda_handler" ]