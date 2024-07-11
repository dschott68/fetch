from aiobotocore import session
import json
import logging

# import localstack_client.session as boto3 # Use this import if you are running in dev without Docker


class SqsQueue:
    """
    Read JSON data containing user login behavior from an AWS SQS Queue, that
    is made available via a custom localstack image that has the data
    pre-loaded.

    https://docs.aws.amazon.com/sqs/

    TODO: Add asynchronous I/O handling and exponential backoff retry logic.
    Use secure method for getting access key. Remove PII data from log
    messages.
    """

    def __init__(
        self, queue_url, endpoint_url, region, aws_access_key_id, aws_secret_access_key
    ):
        self.queue_url = queue_url
        self.endpoint_url = endpoint_url
        self.region = region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=log_format)

    async def read_messages(self):
        """
        Generator function that reads messages from the SQS queue, converts
        each to a dictionary and yields each dictionary. The messages are
        then deleted.
        """
        session = session.get_session()
        async with session.create_client(
            "sqs",
            endpoint_url=self.endpoint_url,
            region_name=self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        ) as sqs:
            response = await sqs.receive_message(QueueUrl=self.queue_url)
            messages = response.get("Messages", [])

            for message in messages:
                logging.debug(f"Message body: {message['Body']}")

                # Convert the message body from JSON to a Python dictionary
                logging.debug(f"Message json: {json.loads(message['Body'])}")

                # yield dict from message body using json.loads
                yield json.loads(message["Body"])

            # Delete the message from the queue
            # Note: You need the ReceiptHandle to delete the message
            receipt_handle = message["ReceiptHandle"]
            await sqs.delete_message(
                QueueUrl=self.queue_url, ReceiptHandle=receipt_handle
            )
            logging.debug(f"Message deleted {receipt_handle}")
        # # Get resource
        # # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html#boto3.session.Session.resource
        # resource = boto3.resource(
        #     "sqs",
        #     endpoint_url=self.endpoint_url,
        #     region_name=self.region,
        #     aws_access_key_id=self.aws_access_key_id,
        #     aws_secret_access_key=self.aws_secret_access_key,
        # )

        # # Get queue
        # # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs/queue/index.html#SQS.Queue
        # queue = resource.Queue(self.queue_url)

        # while True:
        #     # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs/queue/receive_messages.html
        #     messages = queue.receive_messages()

        #     if not messages:
        #         logging.debug("No more messages available")
        #         break

        #     for message in messages:
        #         logging.debug(f"Message body: {message.body}")

        #         # Convert the message body from JSON to a Python dictionary
        #         logging.debug(f"Message json: {json.loads(message.body)}")

        #         # yield dict from message body using json.loads
        #         yield json.loads(message.body)

        #         # Let the queue know that the message is processed
        #         message.delete()
        #         logging.debug(f"Message deleted {message.body}")
