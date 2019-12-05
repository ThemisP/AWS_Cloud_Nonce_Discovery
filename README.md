# AWS Cloud Nonce Discovery
 Cloud Computing, for horizontal scaling of nonce discovery through automated script
 
 # Deployment Process
 1. Create a user with permissions for ec2 and sqs and download the credentials
 1. Launch a new EC2 instance from the AWS console and use the Amazon Linux 2 AMI
 2. Connect to the instance as root user: 
   * install python3
   * install boto3 and awscli (through pip) (pip3 install boto3 awscli --user)
   * change the credentials at the top of main.py script to fit the ones from the user created earlier
   * upload main.py code to the instance
 3. Use the configured instance to create an Amazon Machine Image (right click instance -> Image -> Create new Image)
 4. Create a Key Pair and save the name for Later (recommend to use "cloud_computing" as the name because it is already configured in the scripts)
 5. In local machine configure your aws credentials to be able to connect to your amazon cloud:
   * use aws configure and add the private key and user name of a user that has access to aws cloud
   * also configure the region you want to use
   * both this files are found in ~/.aws/credentials or ~ /.aws/config
 6. In the aws.py script at the top change the keyPairName variable and aws_imageId to fit the key pair and custom AMI created earlier.
 7. run the aws.py script with 3 parameters:
   * python aws.py numberOfLeadingZeros numberOfInstances


# Results
The files containing the output for 16-28 leading zeros from 1-12 instances are contained above and the results are graphed

![Graph of 16 leading zeros](https://github.com/ThemisP/AWS_Cloud_Nonce_Discovery/blob/master/16zeros_graph.png)
![Graph of 20 leading zeros](https://github.com/ThemisP/AWS_Cloud_Nonce_Discovery/blob/master/20zeros_graph.png)
![Graph of 24 leading zeros](https://github.com/ThemisP/AWS_Cloud_Nonce_Discovery/blob/master/24zeros_graph.png)
![Graph of 28 leading zeros](https://github.com/ThemisP/AWS_Cloud_Nonce_Discovery/blob/master/28zeros_graph.png)
