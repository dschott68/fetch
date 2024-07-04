import configparser


class AppConfig:
    """
    This class reads the configuration file and provides the configuration values.
    """

    def __init__(self, config_file_path="config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(config_file_path)

    def get_database_connection_string(self):
        return self.config.get("database", "connection_string")

    def get_sqs_queue_url(self):
        return self.config.get("sqs", "queue_url")

    def get_sqs_endpoint_url(self):
        return self.config.get("sqs", "endpoint_url")

    def get_sqs_region(self):
        return self.config.get("sqs", "region")

    def get_sqs_access_key_id(self):
        return self.config.get("sqs", "aws_access_key_id")

    def get_sqs_secret_access_key(self):
        return self.config.get("sqs", "aws_secret_access_key")
