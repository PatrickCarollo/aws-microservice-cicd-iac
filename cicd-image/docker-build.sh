echo EXECUTING script: docker-build.sh 

#AWS ECR Docker login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $Ecr

#Change directory to source code directory, conditionally.
echo $BUILD_LOCATION
cd $BUILD_LOCATION

#Phase for building and pushing Image to ECR
echo "Building Docker image and pushing to registry: $EcrRepoName..."
docker build -t $EcrRepoName:$UNIQUE_TAG .

#Push to ECR
echo $NEW_IMAGE_URI
docker tag $EcrRepoName:$UNIQUE_TAG $NEW_IMAGE_URI
docker push $NEW_IMAGE_URI
