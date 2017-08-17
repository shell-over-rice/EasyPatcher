#!/usr/bin/env python

import argparse
import boto3
import pprint
import ast


def get_instance_list(filename):
  """ Method to get the list of instances from the file.
  """
  myInstanceList = []
  file = open(filename, 'r')
  for line in file:
    myInstanceList.append(line)
  return myInstanceList 


def get_patch_information(args):
  """ Method to get the patches count in the instances.
      This gives you the count of missing, installed, not applicable
      packages in the instances
  """
  corrected_profile_name = str.lower(args.profile.encode('ascii','ignore'))
  session_3 = boto3.session.Session(profile_name=corrected_profile_name)
  ssm_client = session_3.client('ssm')
  instance_list = get_instance_list(args.patches)
  for instance in instance_list:
    my_id = instance.strip()
    response = ssm_client.describe_instance_patch_states(InstanceIds=[my_id]) 
    pprint.pprint(response)
    #print response
  exit()


def get_detailed_patch_information(args):
  """ Method to get the package level details in the instances.
      This gives you the package name and details in each instance
  """
  corrected_profile_name = str.lower(args.profile.encode('ascii','ignore'))
  session_3 = boto3.session.Session(profile_name=corrected_profile_name)
  ssm_client = session_3.client('ssm')
  instance_list = get_instance_list(args.details)
  for instance in instance_list:
    my_id = instance.strip()
    response2 = ssm_client.describe_instance_patches(
      InstanceId=my_id,
      Filters=[
          {
              'Key': 'State',
              'Values': [
                  'Missing',
              ]
          },
      ]
  )
    pprint.pprint(response2)
  exit()


def scan_instances(args):
  """ Method to scan the instances.
      This allows the system manager to read the packages present in the instance.
      This is a prerequisite and should be the first method executed
  """
  corrected_profile_name = str.lower(args.profile.encode('ascii','ignore'))
  session_1 = boto3.session.Session(profile_name=corrected_profile_name)
  ssm_client = session_1.client('ssm')
  s3_client = session_1.resource('s3')
  response = s3_client.create_bucket(Bucket=args.bucket)
  instance_list = get_instance_list(args.scanlist) 
  for instance in instance_list:
    my_id = instance.strip()
    ssm_command = ssm_client.send_command(InstanceIds=[my_id], DocumentName='AWS-RunPatchBaseline', OutputS3BucketName=args.bucket, Comment='Get patch list from instance', Parameters={"Operation":["Scan"]}) 
  print "Scanning of Instances Completed" 
  exit()


def patch_instances(args):
  """ Method to patch the instances based on associated baseline.
      This allows the user to patch the insances according to the patch baseline 
      associated to the instance. Managing of patch baseline is not in the scope
      of this function
  """
  corrected_profile_name = str.lower(args.profile.encode('ascii','ignore'))
  session_2 = boto3.session.Session(profile_name=corrected_profile_name)
  ssm_client = session_2.client('ssm')
  s3_client = session_2.resource('s3')
  instance_list = get_instance_list(args.patchlist)
  for instance in instance_list:
    my_id = instance.strip()
    ssm_command = ssm_client.send_command(InstanceIds=[my_id], DocumentName='AWS-RunPatchBaseline', OutputS3BucketName=args.bucket, Comment='Get patch list from instance and Install the patches based on baseline defined', Parameters={"Operation":["Install"]})
  print "Patching of Instances Completed"
  exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Track changes to AWS resources.")
    parser.add_argument('--scan',action='store',dest='scanlist',required=False,help='The file name which has list of instances to scan')
    parser.add_argument('--patch',action='store',dest='patchlist',required=False,help='The filename which has list of instances to patch') 
    parser.add_argument('--profile',action='store',dest='profile',required=True,help='The profile name of AWS account')
    parser.add_argument('--bucket',action='store',dest='bucket',required=True,help='The Bucket name to store outputs')
    parser.add_argument('--getpatches',action='store',dest='patches',required=False,help='Get patch details on the instance')
    parser.add_argument('--getdetails',action='store',dest='details',required=False,help='Get patch details at package level on the instance')
    parser.set_defaults(func = scan_instances, func1 = patch_instances, func2 = get_patch_information, func3 = get_detailed_patch_information)
    args = parser.parse_args()
    if args.scanlist:
      args.func(args)
    elif args.patchlist:
      args.func1(args)
    elif args.patches:
      args.func2(args)
    elif args.details:
      args.func3(args)
    else:
      print "Please provide valid arguments"
      exit()
