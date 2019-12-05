import boto3
import time
import botocore
import paramiko


def getTaggedInstances(ec2Client):
    return ec2Client.describe_instances(
        Filters=[
            {
                "Name":"tag:process",
                "Values":["hash"]
            },
            {
                "Name":"instance-state-name",
                "Values":["running"]
            }
        ]
    )

ec2 = boto3.client("ec2")
response = getTaggedInstances(ec2)
print(response)
print(len(response["Reservations"]))