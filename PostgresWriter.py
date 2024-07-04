import psycopg2
from datetime import date


class PostgresWriter:
    """
    PostgresWriter is the class that writes user login data to the Postgres
    database. It uses the psycopg2 library to connect to the database and write
    the data.
    """

    LOGIN_QUERY = """
        INSERT INTO user_logins(
            user_id,
            device_type,
            masked_ip,
            masked_device_id,
            locale,
            app_version,
            create_date
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s
        );
    """

    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = psycopg2.connect(self.connection_string)
        self.cursor = self.connection.cursor()

    def write_user_logins(self, data):
        """
        CREATE TABLE IF NOT EXISTS user_logins(
            user_id varchar(128),
            device_type varchar(32),
            masked_ip varchar(256),
            masked_device_id varchar(256),
            locale varchar(32),
            app_version integer,
            create_date date
        );
        """

        # Convert app_version to integer 2.3.4 becomes 20304
        version_parts = data["app_version"].split(".")
        version_parts = version_parts + [0] * (3 - len(version_parts))
        major, minor, patch = map(int, version_parts)

        app_version = major * 10000 + minor * 100 + patch

        today = date.today()

        if not self.cursor:
            raise Exception("Database connection not initialized")

        # Write data to Postgres
        self.cursor.execute(
            self.LOGIN_QUERY,
            (
                data["user_id"],
                data["device_type"],
                data["masked_ip"],
                data["masked_device_id"],
                data["locale"],
                app_version,
                today,
            ),
        )

        self.connection.commit()
