import boto3
import time
import botocore
import paramiko
import sys
import datetime


aws_imageId="ami-0f4a66714ea2cff7d" # this is for amazon ami, it is an image for an amazon linux instance with python3, awscli and boto3 installed, with the main.py script inside.
securityGroupIds= ["sg-0e0b86b092610b293"] # this is for being able to access the instances through terminals, add a valid security group id.
keyPairName="cloud_computing"
keyPairFileName="cloud_computing.pem"


def createInstance(numberOfInstances, ec2Resource, leadingZeros):
    instances = []
    for i in range(numberOfInstances):
        user_data = '''#!/bin/bash
        python3 /home/ec2-user/main.py ''' +  str(leadingZeros) + " " + str(numberOfInstances) + " " + str(i)
        instances.append(ec2Resource.create_instances(
            ImageId=aws_imageId,
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            KeyName=keyPairName,
            UserData=user_data,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'process',
                            'Value': 'hash'
                        }
                    ]
                }
            ],
            SecurityGroupIds=securityGroupIds
        )[0])
    return instances

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



def checkInstancesStarted(numberOfInstances, ec2Client):
    ## Attempt to see the instances are running and connected 3 times
    for i in range(40):        
        print("Waiting for instances to run...")
        print("seconds: " + str(i*10))        
        time.sleep(10)
        filteredInstances = getTaggedInstances(ec2Client)["Reservations"]
        if(len(filteredInstances)>=numberOfInstances):
            return True
    print("Timed out waiting")
    return False
    
def deleteInstances(instanceList):
    for instance in instanceList:
        instance.terminate()

def executeRemoteCommandinInstances(instanceList, leadingZeros):
    # Create a Key pair in the cloud and download the pem file in the same folder as this script file.
    key = paramiko.RSAKey.from_private_key_file("./"+keyPairFileName)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    instanceNumber = len(instanceList)
    i = 0
    for instance in instanceList:
        instance.load()
        print(instance.public_dns_name)
        # Connect/ssh to an instance
        try:
            # Here 'ubuntu' is user name and 'instance_ip' is public IP of EC2
            client.connect(hostname=instance.public_dns_name, username="ec2-user", pkey=key)
            cmd = "python3 /home/ec2-user/main.py " + str(leadingZeros) + " " + str(instanceNumber) + " " + str(i)
            # Execute a command(cmd) after connecting/ssh to an instance
            stdin, stdout, stderr = client.exec_command(cmd)
            # print(stdout.read())
            print(i)
            # close the client connection once the job is done
            client.close()
        except Exception as e:
            print(e)
        i+=1

def createSQSQueue(sqs):
    # Create the queue for the process
    sqs.create_queue(
        QueueName="cc_queue"
    )

def deleteSQSQueue(sqs):
    queueUrl = sqs.get_queue_url(QueueName="cc_queue")["QueueUrl"]
    sqs.delete_queue(QueueUrl=queueUrl)

def tryToGetAllMessages(sqs, queueUrl, numberOfInstances):
    messagesReceived = 0
    for x in range(5):
        if(messagesReceived>=numberOfInstances):
            return
        for i in range(numberOfInstances-messagesReceived):
            resp = sqs.receive_message(QueueUrl=queueUrl, WaitTimeSeconds=20, MaxNumberOfMessages=10)
            if "Messages" in resp:
                for message in resp["Messages"]:
                    messagesReceived+=1        
                    print(message["Body"])
                    receipt_handle = message["ReceiptHandle"]
                    sqs.delete_message(QueueUrl=queueUrl, ReceiptHandle=receipt_handle)
        time.sleep(1)

def getMessageFromSQS(sqs, numberOfInstances, retries=0):
    if(retries>150):
        print("Waiting for message timed out...")
        return  
    if(retries>0):
        print("Attempting retry number " + str(retries) + " to wait for message.")  
    queueUrl = sqs.get_queue_url(QueueName="cc_queue")["QueueUrl"]
    responses = sqs.receive_message(QueueUrl=queueUrl, WaitTimeSeconds=20, MaxNumberOfMessages=10)
    if "Messages" in responses:
        tryToGetAllMessages(sqs, queueUrl, numberOfInstances)
    else:
        getMessageFromSQS(sqs, numberOfInstances, retries+1)

def purgeSQSQueue(sqs):
    queueUrl = sqs.get_queue_url(QueueName="cc_queue")["QueueUrl"]
    sqs.purge_queue(QueueUrl=queueUrl)

def executeMainProcess(leadingZeros, numberOfInstances):
    ec2Client = boto3.client('ec2')
    ec2Resource = boto3.resource('ec2')
    sqs = boto3.client('sqs')
    createSQSQueue(sqs)
    createdInstances = createInstance(numberOfInstances, ec2Resource, leadingZeros)
    d1 = datetime.datetime.now()
    d2 = d1
    d3 = d1
    print("Instances created!")

    if(checkInstancesStarted(numberOfInstances, ec2Client)):
        print("Instances ready")
        # time.sleep(10) # wait enough time before trying to access instances through ssh
        # print("Sending execute command to instances...")
        # d1 = datetime.datetime.now()
        # executeRemoteCommandinInstances(createdInstances, leadingZeros)
        d2 = datetime.datetime.now()
        print("Waiting for result from any instance...")
        getMessageFromSQS(sqs, numberOfInstances)
        d3 = datetime.datetime.now()

    # print("Time it took from send execute to result: " + str(d3-d1))
    print("Time it took waiting for result: " + str(d3-d2))

    time.sleep(5)
    # deleteSQSQueue(sqs) #either purge or delete sqs queue, both give a 60 second penalty before allowing the same operation on the same queue
    # purgeSQSQueue(sqs)
    deleteInstances(createdInstances)
    print("Deleted Instances")

def batchExecute():
    sys.stdout = open("results_24zeros_v2.txt", "w")
    for i in range(1,13):
        print("------------------------")
        print("Number of instances: " + str(i))
        print("------------------------")
        executeMainProcess(24, i)


def main():
    defaultLeadingZeros = 12
    numberOfInstances = 1
    if(len(sys.argv) > 2):
        convertTemp = int(sys.argv[1], base=10)
        convertTemp2 = int(sys.argv[2], base=10)
        if(convertTemp>0):
            defaultLeadingZeros = convertTemp
        else:
            print("Number of leading zeros entered is incorrect")
            return
        if(convertTemp2>0 and convertTemp2<21):
            numberOfInstances = convertTemp2
        else:
            print("Number of instances entered must be between 1-20")
            return
        executeMainProcess(defaultLeadingZeros, numberOfInstances)
    else:
        print("To execute this script use")
        print("python script.py leadingZeros numberOfInstances")
    


if __name__ == '__main__':
    # batchExecute()
    main()