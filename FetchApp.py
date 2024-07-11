import asyncio
from AppConfig import AppConfig
from PiiMasker import PiiMasker
from PostgresWriter import PostgresWriter
from SqsQueue import SqsQueue
from Validator import Validator
import logging


class FetchApp:
    """
    FetchApp is the main application class that reads messages from an SQS queue,
    masks the PII fields, and writes the data to a Postgres database. It uses the
    AppConfig class to read the configuration file and initialize the components.
    """

    def __init__(self):
        self.app_config = AppConfig("config.ini")

        log_format = "%(asctime)s [%(levelname)s] %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=log_format)

    async def run(self):
        # Initialize the queue, masker, writer and logging
        try:
            queue = SqsQueue(
                self.app_config.get_sqs_queue_url(),
                self.app_config.get_sqs_endpoint_url(),
                self.app_config.get_sqs_region(),
                self.app_config.get_sqs_access_key_id(),
                self.app_config.get_sqs_secret_access_key(),
            )

            pii_masker = PiiMasker()

            postgres_writer = PostgresWriter(
                self.app_config.get_database_connection_string()
            )
            postgres_writer.connect()

            logging.info(f"Startup successful")
        except Exception as e:
            logging.error(f"Startup error: {e}.\nExiting app due to error.")
            return

        # Process messages from the queue
        # TODO: Remove PII data from log messages
        while True:
            messages = await queue.read_messages()

            for message in messages:
                try:
                    logging.debug(f"Processing message: {message}")

                    if not Validator().is_valid_message(message):
                        logging.error(f"Skipping invalid message: {message}.")
                        continue

                    masked_message = pii_masker.mask_all(message)

                    logging.debug(f"Masked message: {masked_message}")

                    postgres_writer.write_user_logins(masked_message)

                    logging.debug(f"Wrote to Postgres: {masked_message}")

                except Exception as e:
                    logging.error(
                        f"Error processing message: {e} for message: {message}."
                    )

            logging.info("Finished processing all messages")


asyncio.run(FetchApp().run())
