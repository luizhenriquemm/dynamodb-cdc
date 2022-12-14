from kafka import KafkaProducer
import boto3, os, uuid, datetime
import simplejson as sjson

def save_as_file(
        arn:str=None,
        path:str=None, 
        data:dict=None):
    """
    This function save the data as a json file;
    """

    if path is None or dict is None:
        raise Exception("Invalid call: Missing one of two attributes. \n Example: save_as_file('s3://bucket/pre/fix/', {'some': 'data'})")
        
    if arn == "":
        arn = None

    protocol = path.split(":")[0]
    if protocol == "s3":
        path = path + "/" if path[-1] != "/" else path
        bucket = path.replace("s3://", "").split("/")[0]
        folder = path.replace(f"s3://{bucket}/", "")
        ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        eventdatepartition = "eventdatepartition=" + ts.split("T")[0] + "/"

        if arn is not None:
            sts = boto3.client('sts').assume_role(RoleArn=arn, RoleSessionName="DataIngestionPipelineSession")
            resource = boto3.resource(
                's3', 
                aws_access_key_id=sts['Credentials']['AccessKeyId'], 
                aws_secret_access_key=sts['Credentials']['SecretAccessKey'],
                aws_session_token=sts['Credentials']['SessionToken'])
        else:
            resource = boto3.resource('s3')

        resource.Object(bucket, folder + eventdatepartition + ts + ".json").put(
            Body=(bytes(sjson.dumps(data).encode('utf-8')))
        )
            
        return f"s3://{bucket}/{folder}{eventdatepartition}{ts}.json"

    else:
        raise Exception(f"The protocol {protocol} is not supported.")
        
def lambda_handler(event, context):
    uuid_v4 = str(uuid.uuid4())
    
    KAFKA_HOSTS = os.getenv('KAFKA_HOSTS', None)
    KAFKA_SERVER_NAME = os.getenv('KAFKA_SERVER_NAME', None)
    OUTPUT_PATH = os.getenv('OUTPUT_PATH', None)
    STS_ROLE_ARN = os.getenv('STS_ROLE_ARN', None)

    print(f"[{uuid_v4}] KAFKA_HOSTS: {KAFKA_HOSTS}")
    print(f"[{uuid_v4}] KAFKA_SERVER_NAME: {KAFKA_SERVER_NAME}")
    print(f"[{uuid_v4}] OUTPUT_PATH: {OUTPUT_PATH}")
    
    if KAFKA_HOSTS is not None:
        KAFKA_HOSTS = KAFKA_HOSTS.split(',')
        credentials = sjson.loads(boto3.client('secretsmanager').get_secret_value(SecretId=KAFKA_SERVER_NAME)['SecretString'])
        producer = KafkaProducer(
                bootstrap_servers=KAFKA_HOSTS,
                security_protocol='SASL_SSL',
                sasl_mechanism="SCRAM-SHA-512",
                sasl_plain_username=credentials['username'],
                sasl_plain_password=credentials['password'],
                acks='all',
                request_timeout_ms=5000,
                max_block_ms=10000,
                api_version=(2, 7, 0),
                value_serializer=lambda v: sjson.dumps(v).encode('utf-8'))
    
    arn = event['Records'][0]['eventSourceARN']
    start = arn.index('table/') + len('table/')
    end = arn.index('/stream/')
    table_name = arn[start:end]

    final_records = []
    for element in event['Records']:
        print(f"[{uuid_v4}] element: {element}")

        deserializer = boto3.dynamodb.types.TypeDeserializer()

        if element['eventName'] in ['MODIFY', 'INSERT']:
            obj = {k: deserializer.deserialize(v) for k,v in element['dynamodb']['NewImage'].items()}
            obj['pipelineEvent'] = element['eventName']
            obj['pipelineEventId'] = element['eventID']
            obj['pipelineEventDate'] = element['dynamodb']['ApproximateCreationDateTime']
            final_records.append(obj)

        elif element['eventName'] == 'REMOVE':
            obj = {k: deserializer.deserialize(v) for k,v in element['dynamodb']['OldImage'].items()}
            obj['pipelineEvent'] = element['eventName']
            obj['pipelineEventId'] = element['eventID']
            obj['pipelineEventDate'] = element['dynamodb']['ApproximateCreationDateTime']
            final_records.append(obj)

        else:
            print(f"[{uuid_v4}] Error to read records. The property eventName isn't mapped! {element}")
            continue

    task_op = { 'Records': final_records }
    print(f"[{uuid_v4}] task_op: ", task_op)
    print(f"[{uuid_v4}] table_name: {table_name}")
    print(f"[{uuid_v4}] events count: {len(final_records)}")

    path = OUTPUT_PATH + "/" if OUTPUT_PATH[-1] != "/" else OUTPUT_PATH
    table_name = str(table_name).lower().replace("-", "_").replace(".", "_")
    final_path = path + table_name + "/"
    print(f"[{uuid_v4}] final_path: {final_path}")
    try:
        file_created = save_as_file(STS_ROLE_ARN, final_path, task_op)
        print(f"[{uuid_v4}] File saved with success: {file_created}")
    except Exception as e:
        print(f"[{uuid_v4}] Error while save_as_file:", str(e))
        print(f"[{uuid_v4}] The data will be send to the Kafka cluster anyway", str(e))

    if KAFKA_HOSTS is not None:
        producer.send(f'dynamodb-cdc-{table_name}', task_op)
        print(f"[{uuid_v4}] Send message - Call flush (wait)")
        producer.flush()
        print(f"[{uuid_v4}] Messages Sent to Kafka Topic")
    else:
        print(f"[{uuid_v4}] KAFKA_HOSTS is not defined, ignored this feature.")

    print(f"[{uuid_v4}] Data processed.")
    return "Data processed."
