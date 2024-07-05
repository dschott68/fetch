class Validator:

    def is_valid_message(self, message):
        """
        Validate the message to ensure it has all the required fields.

        TODO: Add more validation checks including data types, lengths, valid values,
        etc.
        """

        if not message:
            return False

        if not message.get("user_id"):
            return False

        if not message.get("device_type"):
            return False

        if not message.get("ip"):
            return False

        if not message.get("device_id"):
            return False

        if not message.get("locale"):
            return False

        if not message.get("app_version"):
            return False

        return True
