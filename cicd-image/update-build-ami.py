#!/usr/bin/python3
#Executed as a part of the cicd-image cicd,
#Pipeline after the buildspec builds out the new image to include the revised cicd-image code
import os
import boto3
import time
from botocore.exceptions import ClientError
codebuildclient = boto3.client('codebuild')
print('EXECUTING SCRIPT: update-build-ami.py')



#Iterates through all Codebuild Project names and limits only in-scope Projects
def Get_Project_Names():
	try:
		response = codebuildclient.list_projects(
			sortBy = 'CREATED_TIME',
			sortOrder = 'ASCENDING'
		)
		inscope_list = []
		print(response)
		for x in response['projects']:
			if 'Deploymentbuild' in x:
				inscope_list.append(x)
			else:
				pass
		return inscope_list
	except ClientError as e:
		print("Client error: %s" % e)



#Returns entire build project config.. mainly used to get exact project name
def Get_Project_Config(project_name):
	try:
		response = codebuildclient.batch_get_projects(
			names = [project_name]
		)   
		print('Retrieved existing codebuild project: '+project_name)
		return response['projects'][0]
	except ClientError as e:
		print("Client error: %s" % e)
	


#Reset updated fields to supply for update_project- environment.image and project name
def Rebuild_Project_Config(old_config, new_build_ami_uri):
	try:
		old_config['environment']['image'] = new_build_ami_uri
		new_env_object = old_config['environment']
		#Assert new values
		new_config={}
		new_config['name'] = old_config['name']
		new_config['environment'] = new_env_object
		print('Rebuilt with new params on project: '+ old_config['name']+'...')
		print(new_config)
	except:
		print('Failed at Rebuilding to config')
	return new_config


#Issues updated environment object to project
def Update_Project_Ami(new_config):
	time.sleep(6)
	try:
		response = codebuildclient.update_project(
			name = new_config['name'],
			environment = new_config['environment']
		)
		print('Updated: '+ new_config['name'])
		return 'End'
	except ClientError as e:
		print("Client error: %s" % e)



#projectid and new uri will be sent as args through via buildspec to here main()
def main():
	env_variables = os.environ
	global new_build_ami_uri
	new_build_ami_uri = env_variables['NEW_IMAGE_URI']
	#new_build_ami_uri = '058264309078.dkr.ecr.us-east-1.amazonaws.com/myecrmaincore:grow'
	a = Get_Project_Names()
	for x in a:
		b = Get_Project_Config(x)
		c = Rebuild_Project_Config(b,new_build_ami_uri)
		Update_Project_Ami(c)


if __name__ == '__main__':
	main()  
'''
{
  "projects": [
	{
	  "name": "Deploymentbuildmaincore",
	  "arn": "arn:aws:codebuild:us-east-1:058264309078:project/Deploymentbuildmaincore",
	  "source": {
		"type": "CODEPIPELINE",
		"insecureSsl": false
	  },
	  "artifacts": {
		"type": "CODEPIPELINE",
		"name": "Deploymentbuildmaincore",
		"packaging": "NONE",
		"encryptionDisabled": false
	  },
	  "cache": {
		"type": "LOCAL",
		"modes": [
		  "LOCAL_DOCKER_LAYER_CACHE"
		]
	  },
	  "environment": {
		"type": "ARM_CONTAINER",
		"image": "aws/codebuild/amazonlinux2-aarch64-standard:2.0",
		"computeType": "BUILD_GENERAL1_SMALL",
		"environmentVariables": [
		  {
			"name": "Ecr",
			"value": "058264309078.dkr.ecr.us-east-1.amazonaws.com",
			"type": "PLAINTEXT"
		  },
		  {
			"name": "EcrRepoName",
			"value": "myecrmaincore",
			"type": "PLAINTEXT"
		  },
		  {
			"name": "Branch",
			"value": "main",
			"type": "PLAINTEXT"
		  },
		  {
			"name": "projectid",
			"value": "core",
			"type": "PLAINTEXT"
		  }
		],
		"privilegedMode": true,
		"imagePullCredentialsType": "CODEBUILD"
	  },
	  "serviceRole": "arn:aws:iam::058264309078:role/buildpermissionsmaincore",
	  "timeoutInMinutes": 60,
	  "queuedTimeoutInMinutes": 480,
	  "encryptionKey": "arn:aws:kms:us-east-1:058264309078:alias/aws/s3",
	  "tags": [
		{
		  "key": "aws:cloudformation:stack-id",
		  "value": "arn:aws:cloudformation:us-east-1:058264309078:stack/CICDstack-maincore/1b6a5040-2858-11ef-ba69-12f26b876d2d"
		},
		{
		  "key": "aws:cloudformation:stack-name",
		  "value": "CICDstack-maincore"
		},
		{
		  "key": "aws:cloudformation:logical-id",
		  "value": "Buildstage"
		}
	  ],
	  "created": "2024-06-11T21:07:45.368Z",
	  "lastModified": "2024-06-11T21:07:45.368Z",
	  "badge": {
		"badgeEnabled": false
	  },
	  "projectVisibility": "PRIVATE"
	}
  ],
  "projectsNotFound": [],
  "ResponseMetadata": {
	"RequestId": "1ebebad6-16af-4ef1-a483-e95ba3dc4d31",
	"HTTPStatusCode": 200,
	"HTTPHeaders": {
	  "x-amzn-requestid": "1ebebad6-16af-4ef1-a483-e95ba3dc4d31",
	  "content-type": "application/x-amz-json-1.1",
	  "content-length": "1468",
	  "date": "Wed, 10 Jul 2024 17:59:59 GMT"
	},
	"RetryAttempts": 0
  }
}

'''