# DynamoDBChangeDataCapture

When using AWS DynamoDB, you can configure a change data capture structure using other AWS services, this repository contains a model that do this job. You can run all this configuration using AWS CloudFormation, but here we'll keep it simple.

## Enabling the stream in the table

The first step is to enable the stream in the DynamoDB table. In the web interface, find the table in the DynamoDB service and in the "Exports and streams" tab, will be this item:

![image](https://user-images.githubusercontent.com/68759905/207456880-342ea725-bc21-4b57-b61c-d5fe605192c1.png)

Just enable the stream by clicking on the button and you will be asked by the stream type, choose "New and old images" and click "Enable stream":

![image](https://user-images.githubusercontent.com/68759905/207457693-f10c8100-1d70-44aa-85c1-bdebffb5fead.png)

The type "New and old images" provide the both versions of the row, that is usefull for some architetures, the lambda funtion that we are going to use, expect this type of stream. You can change it if you want, but remember to change the script as well.

After that, it will show the stream informations:

![image](https://user-images.githubusercontent.com/68759905/207458048-055fb4b3-feaf-4410-9513-79994caca309.png)

## Creating the lambda function

Before using the stream, it's needed to create the lambda function, in the AWS Lambda service, start a new function like this:

![image](https://user-images.githubusercontent.com/68759905/207459846-f242084e-e774-4e39-b625-ea839fb35d2e.png)

After created, you can update the lambda_function.py script into the function. This script is avaliable here in this repo.

You also need to set the environment variables:

![image](https://user-images.githubusercontent.com/68759905/207466526-371ddf2a-5be5-4979-abd3-b87bcb4aafd2.png)

> **KAFKA_HOSTS**
> A list of kafka servers for sending the daata.

> **KAFKA_SERVER_NAME**
> This variable will be use for getting the secret in the AWS Secrets Manager for the kafka connection.

> **OUTPUT_PATH**
> The lambda function save the data in the kafka topic and in the AWS S3. Here you'll pass the main path for the data, by example, if you use "s3://mybucket/ingestion/" here, the function will append the table name in the path, the data will be saved in "s3://mybucket/ingestion/mytable/".

> **STS_ROLE_ARN**
> The function allows you to save the data in other AWS account, if it's the case, just type the role ARN of the destiny account in this variable and the function will use de S3 of this account. Don't forget that you have to setup the permissions for this.


