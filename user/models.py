from collections.abc import Iterable
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from user.validators import UsernameValidator


class User(AbstractUser):

    username_validator = UsernameValidator()

    username = models.CharField(
        _("username"),
        unique=True,
        max_length=150,
        help_text=_("Required. 150 characters or fewer. Letters, digits and ./+/-/_ only."),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        max_length=256,
        help_text=_("Required. Enter your email address."),
        error_messages={
            "unique": _("A user with that email address already exists."),
        },
    )
    is_verified_email = models.BooleanField(_("is verify"), default=False)
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        if self.is_staff:
            self.is_active = True
        return super().save(*args, **kwargs)