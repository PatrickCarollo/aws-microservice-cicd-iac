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
	a = Get_Project_Names()
	for x in a:
		b = Get_Project_Config(x)
		c = Rebuild_Project_Config(b,new_build_ami_uri)
		Update_Project_Ami(c)


if __name__ == '__main__':
	main()  