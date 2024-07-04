import hashlib


class PiiMasker:
    """
    Fetch wants to hide personal identifiable information (PII). The fields 
    `device_id` and `ip` should be masked, but in a way where it is easy for
    data analysts to identify duplicate values in those fields.

    Use sha256 hash to mask the values of the fields `device_id` and `ip`.
    """
    
    def __init__(self, mask_fields = {"device_id": "masked_device_id", "ip": "masked_ip"}):
        # map of existing fields to mask to new field names
        self.mask_fields = mask_fields

    def mask_all(self, data):
        """
        Mask all fields in the data dictionary that are in the mask_fields map
        replacing the value with the hashed value and renaming the field to the 
        new field name
        """
        for field, new_field in self.mask_fields.items():
            if field in data:
                data[new_field] = self.mask_value(data[field])
                del data[field]

        return data

    def mask_value(self, value):
        return hashlib.sha256(value.encode()).hexdigest()
    
