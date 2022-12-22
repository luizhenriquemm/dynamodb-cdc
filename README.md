# DynamoDB Change Data Capture

Using CDC is a great way for data ingestion, this repository is about a method of doing it in the DynamoDB using only AWS integrated resources.

## How to use it?

I writed an detailed [example here](https://github.com/luizhenriquemm/dynamodb-cdc/blob/main/example.md), but here goes a shorter and simple example:

![Diagram](https://user-images.githubusercontent.com/68759905/209217991-843b66f0-f5c6-461f-befc-af8bee433418.jpg)

The python script that gets executed in the AWS Lambda is [here](https://github.com/luizhenriquemm/dynamodb-cdc/blob/main/lambda_function.py). All the configuration
can be complex for someone that never had it done before, in this case, see the full example, all the step by step is there.
