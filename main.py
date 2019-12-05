import hashlib as hl
import sys
import datetime
import boto3

access_id = "..."
access_key = "..."
region = "..."

def checkLeadingZeros(hash, leadingZeros):
    x = bin(int(hash, 16))[2:].zfill(256)
    if (x+"1").index("1") >= leadingZeros:
        return True
    return False

def hashSHA256Squared(number):
    z = "COMSM0010cloud" + str(number)
    m = hl.sha256()
    m.update(z.encode())
    c = hl.sha256()
    c.update(m.digest())
    return c.hexdigest()

# leadingZeros = number of zeros that need to be in front of a number to be considered a golden nonce
# numberOfinstances and instanceNumber are used to allocate different instances, different numbers to process. 
# For example if we have 4 instances, instance1
def findNonce(leadingZeros, numberOfinstances, instanceNumber):
    i=instanceNumber
    found = 0
    hashFound = ""
    nonceFound = 0
    d1 = datetime.datetime.now()
    while found<1:
        temp = hashSHA256Squared(i)
        if checkLeadingZeros(temp, leadingZeros):
            nonceFound = i
            hashFound = temp
            found += 1
        i += numberOfinstances
    d2 = datetime.datetime.now()
    # print("Start timestamp %s" %d1)
    # print("End timestamp %s" %d2)
    # print("Elapsed Time: %s" %(d2-d1))
    # print("Hash: " + hashFound)
    # print("Nonce: " + str(nonceFound))
    sqs = boto3.client(
        'sqs',
        aws_access_key_id=access_id,
        aws_secret_access_key=access_key,
        region_name=region
    )
    queueUrl = sqs.get_queue_url(QueueName="cc_queue")["QueueUrl"]
    sqs.send_message(QueueUrl=queueUrl, MessageBody=("Time: " + str(d2-d1) + " Nonce: " + hashFound + " Number used: " + str(nonceFound)))

def main():
    # for arg in sys.argv[1:]: #this is for commant line arguments
    #     print(arg)
    defaultLeadingZeros = 8
    numberOfInstances = 1
    instanceNumber = 0
    if(len(sys.argv) > 3):
        convertTemp = int(sys.argv[1], base=10)
        convertTemp2 = int(sys.argv[2], base=10)
        convertTemp3 = int(sys.argv[3], base=10)
        if(convertTemp>0):
            defaultLeadingZeros = convertTemp
        if(convertTemp2>0):
            numberOfInstances = convertTemp2
        if(convertTemp3>0):
            instanceNumber = convertTemp3
    findNonce(defaultLeadingZeros, numberOfInstances, instanceNumber)

if __name__ == '__main__':
    main()
    
    