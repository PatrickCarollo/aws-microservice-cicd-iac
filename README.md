# Serverless Microservice + CI/CD Deployment
Leveraging IaC tools on AWS for the setup of a set of services that includes a serverless microservice Docker image Lambda,
Rest API endpoint, and CI/CD pipeline.


## Brief Architectural Outline
This project as-is, manages/deploys serverless application and infrastructure 
with an included CI/CD process. Using AWS SAM to deploy initial core app services like exposing API endpoint with Lambda 
Proxy Integration to process request data, an S3 bucket and NOSQL DB. The project associates these corresponding
application resources to CI/CD resources using unique IDs in resource name (input stack params provided upon setup).
A python script "Configure.py" initiates setup of base CI/CD infrastructure like fetching
IAM roles, base S3 bucket creation for storing source code of Codepipeline custom actions and CloudFormation stack launch
(setting stack input parameters). The CI/CD Infrastructure
consists of leveraging CodePipeline stages(Codebuild for automation of Docker image pushes to ECR and Lambda 
for testing and deployment phases) and can be conditionally setup with source provider as 
either an existing Github repo or a new Codecommit repo.

## Pre setup notes:
+ you'll set `projectid` to a short string describing the microservice use
and `sourcebranch` to either `main` or `dev`. They're used to
isolate ci/cd pipelines as well as associate ci/cd services to their corresponding target services
+ If using GitHub as code source provider:
    - A Connection should be setup for the desired account in Console at Codepipeline>Settings>Connections
+ Per each microservice- An existing Repository with Git branch named `dev` or `main` 
    should exist before launching CI/CD stack

## Setup Instructions
1. Copy directories from this repository to desired new microservice repository
    ```
    cp -r aws-microservice-cicd-iac/cicd-services <yourreponame>/
    ```
    ```
    cp -r aws-microservice-cicd-iac/api-services <yourreponame>/
    ```
    - Move <yourreponame>/cicd-services/buildspec.yaml to root of <yourreponame>
    - Change location of lambda stages' code by modifying the root folder name in Upload_Resources() to match your new   repo

2. Install/update SAM CLI 
    ```
    install sam cli
    ```

3. Create a private ECR in AWS console. __ECR naming format:__ `<nameofyourchoosing><sourcebranch><projectid>`

4. Sign into docker using aws auth, build desired initial starting docker image, push
   *Skip build if you already have Image or launching for development stack
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
    docker push <yourawsacountid>.dkr.ecr.<yourawsregion>.amazonaws.com/<yourECRname:latest
    ```
    
5. Deploy microservice stack(from api-services)
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

7. Run `Configure.py` script in aws-microservice-cicd-iac and enter input prompts- use the same `projectid` param as entered in SAM microservice stack to associate CI/CD services 

8. Push a change to source repository branch and check AWS Codepipeline console to verify pipeline exection- as well
as Lambda>Alias>Versions to check if the new version was deployed.

## Maintenance and Limitations 05/17/24:
This infrastructure is obviously only intended to configure BASE infrastructure for a simple application. It is meant to be built ontop of, for example; auth for the api endpoints, bucket policies, and fine-tuning rate limits on the lambda function all could be considerations that are not (yet) included in this project.
Other considerations and refactoring notes; 
1. S3 bucket and dynamodb database is currently being deployed in app stack. 
    This Resource(s) might be elected for removal if creating for example if deploying a list or get feature-
    These would need reworking or remove as well as references to these resources in ci/cd stack template.yml.
2. lambda-action1 code- it's test request is formed for specific mock request parameters that should be changed. 
3. Looking to refactor the services defined cicd-template.yml to be deployable without having the prerequisite microservices stack deployed. This would be to make the ci/cd portion of this repository usable as a standalone set of services for an already existing lambda function setup



## Contents Description: 
`Configure.py`: Prerequisite configuration script for launching CICD stack.
Deploys resource bucket for subsequent Cloudformation Template launch. It accepts runtime inputs that are passed into 
stack creation call as Parameters for cicd-template.yml.

`api-services/template.yml`: SAM Template for deploying application services and 
creates stack Output Parameters from the resulting launched service's ARNs for cicd-template.yml to import.
Sets up the following:  
* User S3 storage bucket, 
* DynamoDB user database table that application code will write to,
* Api Gateway Rest API integrated with Lambda as compute service & Alias to manage versions.
    This configuration is setup to forward API requests to Lambda Live Alias.

`CICDLambda/cicd-template.yml`:  Cloudformation Template for deploying CI/CD process' core services by launching a Codepipeline pipeline 
and it's underlying stages. This template can be conditionally run based on parameters passed in at launch 
from Configure.py script. All stages' services are deployed along with respective IAM Service Roles granting least 
privelage access. The conditional launches are for using github or aws as source repository as well as setting source branch.
Stack constists of: 
* Codecommit or GitHub Connection(github connection required) as source repository 
* Codebuild Project with a Linux container for running build commands
    commands on the ingested source artifacts(Dockerfile) and creating a temp Lambda Version
* Lambda Test action lambda-action1.py for creating and sending sample request through the temp lambda version to validate revision
* Lambda Action lambda-action2.py as last stage in pipeline for creating CodeDeploy Deployment on Group using revision object. 
    This works by updating the Alias Version # that the API is forwarding requests to and promoting it to main version.
`sourcecode/aws_handler`: Sample core application code that parses request data and runs logic






