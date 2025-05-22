# Serverless Microservice + CI/CD Deployment
Infrastructure setup for AWS Lambda microservice API and Codepipeline CI/CD.


## Architectural Overview
This project delivers a comprehensive serverless microservice framework that combines AWS Lambda applications with fully automated CI/CD pipelines. The architecture solves the common challenge of deploying and managing multiple microservices consistently and maintains security standards and operational efficiency. It uses AWS Serverless Application Model(SAM) to deploy initial services such as; API Gateway endpoint w/ Lambda Proxy Integration. It includes a centralized locally run python script "cicd-deploy-tool.py" that deploys and manages the CI/CD infrastructure. The deployment process is executed and managed as a Codepipeline/ Codebuild Project running a custom Image. There are two CI/CD processes includes- one for Lambda as well as for a global custom Build Image. Which flow is run is dictated by parsing the GIT Commit message.

## Features
- All core services for a working API endpoint and simple application
    - Configs for services S3, DynamoDB, API Gateway and Lambda(and all the necessary IAM Service Roles)
- Full CI/CD process for a Docker Image Lambda 
    - Process is packaged as a Codebuild Custom AMI and contains python and Bash scripts for; building out a new Docker Image, Uploading to ECR, creating new Lambda version, running a test script and upon success promote the version to live.
- Single point CI/CD Services deployment
    - Configure.py acts as a deployment script for deploying and managing the IaC Cloudformation Stacks that define the
    Codepipeline and underlying configurations
- Isolated services
    - This system when deployed configures a single Lambda application and respective CI/CD pipeline. But it has the capability to be deployed for several features or apps and each would be isolated. You would just run the deployment setup process again but with different projectid value
- Global Build and Deploy AMI
    - Uses a single Codebuild Custom Image designed to be shared across all associated projects.
    This simplifies the need to custom remake build and deployment scripts for every new feature and add to every repository. It accomplishes this by referencing the Codebuild Custom Image Uri(your ECR).
- CI/CD process for the Custom AMI
    - The code for the AMI is hosted in the first repository registered and this repository's pipline will have the capability to efficiently roll out changes to the global custom Image.
    The Build and Deploy Container itself parses out the commit message and if it is 'builder update' it builds and deploys out from the Codebuild Dockerfile then updates all of the Codebuild projects URI to use this new image.

## Pre setup notes:
+ `projectid` is intended to be set as a short string describing the microservice use
and `sourcebranch` to either `main` or `dev`. They're used to
isolate ci/cd pipelines as well as associate ci/cd services to their corresponding target services
+ If using GitHub as code source provider:
    - A Github repository and then a Connection should be setup for the desired account in Console at Codepipeline>Settings>Connections
+ Per each microservice- An existing Repository with Git branch named `dev` or `main` 
    should exist before launching CI/CD stack
+ The first repository registered for this project is designed to act as the source of the global build image
+ Consider adding environment variables for application in api-services/src/template.yml
## Setup Instructions
1. Copy directories from this repository to desired new source microservice repo
    ```
    cp -r aws-microservice-cicd-iac/cicd-image <yourreponame>
    ```
    *Only copy ^^cicd-image^^ folder if this is the first repo registered- acts as global source for shared build image
    ```
    cp -r aws-microservice-cicd-iac/cicd-services <yourreponame>
    ```
    ```
    cp -r aws-microservice-cicd-iac/api-services <yourreponame>
    ```
    ```
    cp aws-microservice-cicd-iac/buildspec.yml <yourreponame>
    ```
2. Install/update SAM CLI 
    ```
    install sam cli
    ```

3. Create a private ECR in AWS console. 

4. Sign into docker using aws auth, build desired initial starting docker image, push
   *Skip Docker build commands if you already have a local Image(launching for development stack)- but you must specify a ECR URI. This establishes respective variables
    ```
    cd <yourreponame>/api-services/src
    ```
    ```
    docker build -t <yourECRname> .
    ```
    ```
    aws ecr get-login-password --region <yourawsregion> | docker login --username AWS --password-stdin <ecr uri>
    ``` 
    ```
    docker tag <imageid> <ecr uri>:latest
    ```
    ```
    docker push <ecr uri>:latest
    ```
    * Repeat for the build image if first repo
    
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
                    "ecr:DescribeImages",
                    "ecr:ListImages",
                    "ecr:BatchGetImage",
                    "ecr:DescribeRegistry",
                    "ecr:DescribeRepositories"
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
This system is only intended to configure BASE infrastructure for a simple serverless application. It is meant to be built ontop of, for example; auth for the api endpoints, rate limits, bucket policies, could be considerations that are not addressed in the current configuration.
Other considerations and refactoring notes; 
1. S3 bucket and dynamodb database is currently being deployed in app stack. 
    This Resource(s) might be elected for removal if creating for example if deploying a list or get feature-
    These would need reworking or remove as well as references to these resources in ci/cd stack template.yml.
2. lambda-action1 code- it's test request is formed for specific mock request parameters that should be changed. 
3. Looking to refactor the services defined cicd-template.yml to be deployable without having the prerequisite microservices stack deployed. This would be to make the ci/cd portion of this repository usable as a standalone set of services for an already existing lambda function setup








