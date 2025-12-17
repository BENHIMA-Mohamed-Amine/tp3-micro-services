import pytest
from pydantic import ValidationError
from app.models import CustomerCreate, CustomerUpdate


def test_customer_create_validation_empty_name():
    with pytest.raises(ValidationError):
        CustomerCreate(name="", email="a@b.com")


def test_customer_create_validation_bad_email():
    with pytest.raises(ValidationError):
        CustomerCreate(name="John", email="not-an-email")


def test_customer_update_optional_fields_validation():
    # No fields provided is allowed (all optional)
    cu = CustomerUpdate()
    assert cu.name is None
    assert cu.email is None


import pytest
from pydantic import ValidationError
from app.models import CustomerCreate, CustomerUpdate


def test_customer_create_validation_empty_name():
    with pytest.raises(ValidationError):
        CustomerCreate(name="", email="a@b.com")


def test_customer_create_validation_bad_email():
    with pytest.raises(ValidationError):
        CustomerCreate(name="John", email="not-an-email")


def test_customer_update_optional_fields_validation():
    # No fields provided is allowed (all optional)
    cu = CustomerUpdate()
    assert cu.name is None
    assert cu.email is None
