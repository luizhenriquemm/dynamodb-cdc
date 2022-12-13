# DynamoDBChangeDataCapture

When using AWS DynamoDB, you can configure a change data capture structure using other AWS services, this repository contains a model that do this job. You can run all this configuration using AWS CloudFormation, but here we'll keep it simple.

The first step is to enable the stream in the DynamoDB table. In the web interface, find the table in the DynamoDB service and in the "Exports and streams" tab, will be this item:

![image](https://user-images.githubusercontent.com/68759905/207456880-342ea725-bc21-4b57-b61c-d5fe605192c1.png)

Just enable the stream by clicking on the button and you will be asked by the stream type, choose "New and old images" and click "Enable stream":

![image](https://user-images.githubusercontent.com/68759905/207457693-f10c8100-1d70-44aa-85c1-bdebffb5fead.png)

After that, it will show the stream informations:

![image](https://user-images.githubusercontent.com/68759905/207458048-055fb4b3-feaf-4410-9513-79994caca309.png)

a
