import os
import boto3
import datetime

start_date = str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
autoScalingGroupName = os.environ['Auto_Scaling_Group_Name']
launchTemplateName = os.environ['Launch_Template_Name']
ec2RoleARN = os.environ['EC2_Role_ARN']
keyName = os.environ['Private_Key_Name']
ec2SecurityGroupID = os.environ['EC2_Security_Group_ID']

def lambda_handler(event, context):
    
    try:
        client = boto3.client('autoscaling')
        autoscaling = client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[
            autoScalingGroupName
            ]
        )

        instanceID = autoscaling['AutoScalingGroups'][0]['Instances'][0]['InstanceId']
        client = boto3.client('ec2')
        name= "Lambda for " + autoScalingGroupName + " from "+ start_date
        description= "AMI for " + autoScalingGroupName + " created by lambda"

        image = client.create_image(
            Description=description,
            DryRun=False, 
            InstanceId=instanceID, 
            Name=name)

        launch_template= client.create_launch_template_version(
            DryRun=False,
            LaunchTemplateName = launchTemplateName,
            VersionDescription = name,
            LaunchTemplateData={
                'IamInstanceProfile': {
                    'Arn': ec2RoleARN
                },
                'ImageId': image['ImageId'],
                'KeyName': keyName,
                'SecurityGroupIds': [
                    ec2SecurityGroupID,
                ]
            }
        )
        
        job_id = event["CodePipeline.job"]["id"]
        pipeline = boto3.client('codepipeline')
        response = pipeline.put_job_success_result(jobId=job_id)
        
        return True
        
    except Exception as e:
        print(e)
        
    
        job_id = event["CodePipeline.job"]["id"]
        pipeline = boto3.client('codepipeline')
        response = pipeline.put_job_failure_result(
            jobId=job_id,
            failureDetails={
                'type': 'JobFailed',
                'message': e
            }
        )

            
        return False