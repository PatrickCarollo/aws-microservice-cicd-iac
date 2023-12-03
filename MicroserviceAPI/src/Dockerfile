#Python 
FROM python:3.8

#Set the working directory to /src 
WORKDIR /src

#Copy local code and dependencies to the container
COPY . .

#Install any needed packages
RUN pip install --no-cache-dir -r requirements.txt

#Command to run on container start
CMD [ "python", "aws_handler.py", "lambda_handler" ]