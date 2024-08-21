echo EXECUTING SCRIPT: update-lambda-uri.sh
aws lambda update-function-code \
    --function-name $LambdaName \
    --image-uri $NEW_IMAGE_URI \
    --publish
