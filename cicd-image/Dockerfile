#Official Docker image as a parent image..
FROM docker:20.10-dind

#System dependencies install
RUN apk add --no-cache \
    python3 \
    py3-pip \
    git \
    bash \
    && pip install --upgrade pip \
    && pip install boto3 awscli

#Set working directory for ci/cd scripts
WORKDIR /code

#Copy all code to container
COPY . ./

#Set execute permissions for scripts
RUN chmod +x docker-build.sh promote-to-live.py update-build-ami.py update-lambda-uri.sh test-request.py

#NOT NECESSARY IN CODEBUILD DOCKERFILE- codebuild does not run CMD on container start. Starts Docker daemon and ensures docker is available hosts
#CMD ["sh", "-c", "nohup dockerd --host=unix:///var/run/docker.sock --host=tcp://127.0.0.1:2375 --storage-driver=overlay2 &"]

#Adds /code to Path list for calling build/deploy scripts from any directory
ENV PATH="/code:${PATH}"