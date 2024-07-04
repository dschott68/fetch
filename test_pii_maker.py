import pytest
from PiiMasker import PiiMasker


def test_mask_value():
    pii_masker = PiiMasker()
    assert (
        pii_masker.mask_value("a_test_value")
        == "66107e5ac3464ce948b9a1b2164f54a4f3e3dc450e54bd4bdafaee856733aa1f"
    )


def test_mask_all():
    pii_masker = PiiMasker()
    data = {"device_id": "a_test_value", "ip": "another_test_value"}
    assert pii_masker.mask_all(data) == {
        "masked_device_id": "66107e5ac3464ce948b9a1b2164f54a4f3e3dc450e54bd4bdafaee856733aa1f",
        "masked_ip": "62861c5b8bc4cb6f8c28052be3c2d70c96d07c8a15ba99d2bc81513e81084e12",
    }
