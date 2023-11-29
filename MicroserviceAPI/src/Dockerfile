# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory to /app
WORKDIR /src

# Copy the local code and dependencies to the container
COPY . .


# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#Command to run on container start
CMD [ "aws_handler.lambda_handler" ]
