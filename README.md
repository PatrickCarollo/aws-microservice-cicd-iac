# Serverless Microservice + CI/CD Deployment
Infrastructure setup for AWS Lambda microservice API and Codepipeline CI/CD.


## Architectural Overview
This project as-is, manages and deploys a serverless application and associated services 
with an included CI/CD process. It uses AWS Serverless to deploy initial core microservice such as; API Gateway endpoint w/ Lambda Proxy Integration. A python script "cicd-deploy-tool.py" initiates setup of the CI/CD infrastructure. There are two CI/CD flows- one for Lambda as well as for a global custom Build Image. Which flow is run is decided by parsing the Git commit message. 
The scripts flow for automating Lambda deployment;
docker-build.sh: Building and pushing a new Docker image from revision(this can be both Lambda Image or Build Image)>
update-lambda-uri.sh: Creates a 'temp' version on Core Lambda Function
test-requst.py: Sends a mock event directly to the newest Core Lambda version>
promote-to-live.py: Promotes the revised Lambda to Live upon successful test. It does this the by updating the Alias number, which API Gateway forwards requests to, to the revised, tested version.
The scripts flow for automating Build Image updates:
docker-build.sh>
update-build-ami.py: Updates the Image URI that Codebuild is using as Project Image



## Pre setup notes:
+ `projectid` will be set to a short string describing the microservice use
and `sourcebranch` to either `main` or `dev`. They're used to
isolate ci/cd pipelines as well as associate ci/cd services to their corresponding target services
+ If using GitHub as code source provider:
    - A Github repository and then a Connection should be setup for the desired account in Console at Codepipeline>Settings>Connections
+ Per each microservice- An existing Repository with Git branch named `dev` or `main` 
    should exist before launching CI/CD stack
+ The first repository registered for this project is designed to act as the source of the global build image
## Setup Instructions
1. Copy directories from this repository to desired new source microservice repo
    ```
    cp -r aws-microservice-cicd-iac/cicd-image <yourreponame>
    ```
    *Only copy ^^this^^ folder if this is the first repo registered- acts as source for build image
    cp -r aws-microservice-cicd-iac/cicd-services <yourreponame>
    ```
    ```
    cp -r aws-microservice-cicd-iac/api-services <yourreponame>
    ```
    ```
    cp aws-microservice-cicd-iac/buildspec.yml <yourreponame>

2. Install/update SAM CLI 
    ```
    install sam cli
    ```

3. Create a private ECR in AWS console. 

4. Sign into docker using aws auth, build desired initial starting docker image, push
   *Skip build cmd if you already have a local Image(launching for development stack)- but you must specify a ECR URI. This establishes respective variables
    ```
    cd <yourreponame>/api-services/src
    ```
    ```
    docker build -t <yourECRname> .
    ```
    ```
    aws ecr get-login-password --region <yourawsregion> | docker login --username AWS --password-stdin <yourawsaccountid>.dkr.ecr.<yourawsregion>.amazonaws.com
    ``` 
    ```
    docker tag <imageid> <yourawsaccid>.dkr.ecr.<yourawsregion>.amazonaws.com/<yourECRname>:latest
    ```
    ```
    docker push <yourawsacountid>.dkr.ecr.<yourawsregion>.amazonaws.com/<yourECRname>:latest
    ```
    * Do the same for the build image if first repo
    
5. Deploy microservice stack(from /api-services)
    ```
    cd ../
    ```
    ```
    sam build
    ```
    ```
    sam deploy --guided
    ```
    * Fill in SAM prompts & template parameters.. __stack name format:__ `microservicestack<sourcebranch><projectid>`
    * Check AWS Cloudformation console to verify the launch status

6. Create CI/CD stack service role. Run following CLI cmds.

    ```
    aws iam create-role --role-name MainCICDStackServiceRole --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudformation.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }'
    ```
    ```
    aws iam put-role-policy --role-name MainCICDStackServiceRole --policy-name MainCICDStackServicepolicy --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "codecommit:CreateBranch",
                    "codecommit:CreateRepository",
                    "codecommit:DeleteRepository",
                    "codecommit:DeleteBranch",
                    "codecommit:CreateCommit",
                    "codecommit:ListRepositories",
                    "codecommit:GetRepository",
                    "lambda:CreateFunction",
                    "lambda:DeleteFunction",
                    "lambda:GetFunction",
                    "lambda:PublishVersion",
                    "lambda:DeleteAlias",
                    "lambda:CreateAlias",
                    "codedeploy:CreateApplication",
                    "codedeploy:CreateDeploymentConfig",
                    "codedeploy:CreateDeploymentGroup",
                    "codepipeline:CreatePipeline",
                    "codepipeline:GetPipeline",
                    "codepipeline:DeletePipeline",
                    "codepipeline:GetPipelineState",
                    "codedeploy:DeleteDeploymentConfig",
                    "codedeploy:GetDeploymentGroup",
                    "codedeploy:DeleteGitHubAccountToken",
                    "codedeploy:DeleteApplication",
                    "codedeploy:DeleteDeploymentGroup",
                    "events:EnableRule",
                    "events:PutRule",
                    "events:DeleteRule",
                    "events:PutEvents",
                    "events:DescribeRule",
                    "events:PutTargets",
                    "events:RemoveTargets",
                    "s3:CreateBucket",
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject",
                    "s3:DeleteBucket",
                    "iam:CreateRole",
                    "iam:UpdateRole",
                    "iam:GetRole",
                    "iam:DeleteRole",
                    "iam:PutRolePolicy",
                    "iam:DetachRolePolicy",
                    "iam:DeleteRolePolicy",
                    "iam:AttachRolePolicy",
                    "iam:PassRole",
                    "codebuild:ListProjects",
                    "codebuild:DeleteProject",
                    "codebuild:CreateProject",
                    "codebuild:BatchGetProjects",
                    "codebuild:UpdateProject"
                    "codedeploy:DeleteDeploymentConfig",
                    "codedeploy:GetDeploymentGroup",
                    "codedeploy:DeleteGitHubAccountToken",
                    "codedeploy:DeleteApplication",
                    "codedeploy:DeleteDeploymentGroup",
                    "codestar-connections:PassConnection",
                    "codestar:*"
                ],
                "Resource": "*"
            }
        ]
    }'
    ```

7. Run `cicd-deploy-tool.py` script in aws-microservice-cicd-iac and enter input prompts- use the same `projectid` param as entered in SAM microservice stack to associate CI/CD services 

8. Push a change to source repository branch and check AWS Codepipeline>Codebuild console Logs to verify pipeline exection-
 and Lambda>Alias>Versions to check if the new version was deployed and promoted.

## Maintenance and Limitations 05/28/24:
This infrastructure is obviously only intended to configure BASE infrastructure for a simple application. It is meant to be built ontop of, for example; auth for the api endpoints, bucket policies, and fine-tuning rate limits on the lambda function all could be considerations that are not (yet) included in this project.
Other considerations and refactoring notes; 
1. S3 bucket and dynamodb database is currently being deployed in app stack. 
    This Resource(s) might be elected for removal if creating for example if deploying a list or get feature-
    These would need reworking or remove as well as references to these resources in ci/cd stack template.yml.
2. lambda-action1 code- it's test request is formed for specific mock request parameters that should be changed. 
3. Looking to refactor the services defined cicd-template.yml to be deployable without having the prerequisite microservices stack deployed. This would be to make the ci/cd portion of this repository usable as a standalone set of services for an already existing lambda function setup








