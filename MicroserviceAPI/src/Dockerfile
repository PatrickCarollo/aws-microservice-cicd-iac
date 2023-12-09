#Python location in managed Codebuild Linux
FROM public.ecr.aws/lambda/python:latest

#Copy local code  to the container
COPY aws_handler.py ${LAMBDA_TASK_ROOT}

#Install any needed dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

#Command to run on container start
CMD [ "aws_handler.lambda_handler" ]