"""BaseModel module

This module defines a simple abstract base model that any other
Django models in the project can inherit from. It provides
automatic timestamp fields for creation and last update.
"""

from django.db import models


class BaseModel(models.Model):
    """Abstract base class providing timestamp fields.

    Attributes:
        created_at (datetime): Automatically set to the time when an
            instance is first created.
        updated_at (datetime): Automatically updated to the current time
            whenever the instance is saved.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the base model.

        Declares the model as abstract so that no database table is created
        for this class itself. Other models will inherit its fields.
        """

        abstract = True
