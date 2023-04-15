# AWS-MS-Infrastructure
Deploys infrastructure for an AWS Lambda application with and CI/CD. 




OUTLINE:

Deploys the core app stack('template.yaml) using Serverless Application Model that contains; A simple nosql
database with dynnamoDB and configures an index and several basic attributes,
Lambda function deployed with simple test code, an api gateway Rest Api configured with as Lambda as proxy integration, 
an application user S3 bucket, and necessary IAM service roles for each.
The CI/CD stack (template0.yaml) which is deployed though 'configure.py contains core services for a CI/CD
pipeline such as; conditional repository provider setup- either GItHub or CodeCommit - an EventBridge rule for source changes 
in the repository or if using github a push event, a CodeBuild build stage using Linux container 
for zipping and deploying code to development lambda version according to a buildspec.yaml file, 
a test action that will send a test request directly to this version, and a deployment stage that uses lambda to
create a CodeDeploy deployment that shifts traffic to new tested version.
All of these CI/CD stages are then incorperated into CodePipeline service configured in the stack along with all necessary IAM service roles.


Prereqs and deploy Instructions:
    1. Create IAM role by running CLI commands provided in 'ServiceRoleCLICommands.txt'.
    2. Optionally have CodePipeline 3rd party connections enabled(GitHub). 
        this can be done as a Codestar connection in CodePipeline console.
    3. Run sam build, sam deploy commands in directory 'AWS-MS-Infratructure/MicroserviceAPI' and name stack 'microservicestack'.
    4. Run 'Configure.py' create command for CI/CD provisions deployment.
    5. Done. Check console for functionality.
