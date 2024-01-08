# Serverless Microservice + CI/CD Deployment
Leveraging IaC tools on AWS for the setup of serverless microservice application that processes images 
and string parameters delivered via Rest API supported by CI/CD pipeline.


## Brief Architectural Outline
This project as-is, manages/deploys serverless application and infrastructure 
with a built-in CI/CD process. Using AWS SAM to deploy initial core app services like Exposing API endpoint with a Lambda 
Proxy Integration to process request data, an S3 bucket and NOSQL DB. The project associates these corresponding
application resources to CI/CD resources using a unique IDs in resource name (input string params provided upon setup)
A python script "Configure.py" initiates setup of base CI/CD infrastructure like fetching
IAM roles, base S3 bucket creation for storing source code of Codepipeline custom actions and Cloudformation stack launch(setting stack input parameters). The CI/CD Infrastructure
consists of leveraging CodePipeline stages(Codebuild for automation of Docker image pushes to ECR and Lambda 
for testing and deployment phases) and can be conditionally setup with source provider as 
either an existing Github repo or a new Codecommit repo.

## Pre setup notes:
+ set parameters `projectid` to a short string describing the function
and `sourcebranch` to either `main` or `dev`. They're used to
isolate ci/cd pipelines as well as associate ci/cd services to their corresponding target services
+ If using GitHub as code source provider:
    - An existing Git branch named `dev` must exist before launching CI/CD stack in dev branch support launch
    - `/scr` directory AND buildspec.yml should be copied to root 

## Setup Instructions:
1. Install/update SAM CLI 

2. Create a private ECR in AWS console. __ECR naming format:__ `<nameofyourchoosing><sourcebranch><projectid>`

3. Sign into docker using aws auth, build desired initial docker image, push
   *Skip docker build if you've refactored (see Maintenance and Limitations) and already have an Image you'd like to use
    ```
    cd aws-microservice-cicd-iac/MicroserviceAPI/src
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
    
4. Deploy microservice stack
    ```
    cd aws-microservice-cicd-iac/MicroserviceAPI
    ```
    ```
    sam build
    ```
    ```
    sam deploy --guided
    ```
    * Fill in SAM prompts & template parameters.. __stack name format:__ `microservicestack<sourcebranch><projectid>`
    * Check AWS Cloudformation console to verify the launch status

5. Create CI/CD stack service role. Run following CLI cmds.

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
        "Statement":
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

6. Run `Configure.py` script and enter input prompts- use the same `projectid` param as entered in SAM microservice stack to associate
CI/CD services 

7. Push a change to source repository branch and check AWS Codepipeline console to verify pipeline exection

## Maintenance and Limitations 11/28/23:
This infrastructure is intended to configure BASE infrastructure for- meaning only core functionality
is included and is meant to be built ontop of, For example; setting up security on prod stack. This set of resources, as-is, is
only architected for a single monolithic service. Considerations when refactoring for separate features; 
1. S3 bucket and dynamodb database is currently being deployed in app stack. 
    This Resource(s) might be elected for removal if creating for example if deploying a list or get feature-
    These would need reworking or remove as well as references to these resources in ci/cd stack template.yml.
2. lambdaAction1 code- how its test request is formed for specific mock request parameters. 



## Contents Description: 
`Configure.py`: Prerequisite configuration script for launching CICD stack- 
deploys resource bucket for subsequent Cloudformation Template launch. It accepts runtime inputs that are passed into 
stack creation call as Parameters for template0.yml.

`MicroserviceAPI/template.yml`: SAM Template for deploying application services and 
creates stack Output Parameters from the resulting launched service's ARNs for template0.yml to import.
Sets up the following:  
* User S3 storage bucket, 
* DynamoDBuser database table that application code will write to,
* Api Gateway Rest API integrated with Lambda as compute service & Alias to manage versions.
    This configuration is setup to forward API requests to Lambda Live Alias.

`CICDLambda/template0.yml`:  Cloudformation Template for deploying CI/CD process' core services by launching a Codepipeline pipeline 
and it's underlying stages. This template can be conditionally run based on parameters passed in at launch 
from Configure.py script. All stages' services are deployed along with respective IAM Service Roles granting least 
privelage access. The conditional launches are for using github or aws as source repository as well as setting source branch.
Stack constists of: 
* Codecommit or GitHub Connection(github connection required) as source repository 
* Codebuild Project with a Linux container for running build commands
    commands on the ingested source artifacts(Dockerfile) and creating a temp Lambda Version
* Lambda Test action LambdaAction1.py for creating and sending sample request through the temp lambda version to validate revision
* Lambda Action LambdaAction2.py as last stage in pipeline for creating CodeDeploy Deployment on Group usinga  revision object. 
    This works by updating the Alias Version # that the API is forwarding requests to.
`sourcecode/aws_handler`: Core application code that parses request data and runs logic- This should be integrated
into a Dockerfile if using lambda package type as Image and not code.zip 






