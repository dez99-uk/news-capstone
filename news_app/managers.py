"""Custom model managers used by the news application.

The custom user manager centralises user and superuser creation so that
validation and role defaults are applied consistently throughout the project.
"""

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Manage creation of standard users and superusers.

    This manager normalises email addresses, validates required fields, and
    applies default flags for privileged accounts.
    """

    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """Create and persist a user instance.

        Args:
            username (str): Unique username used for authentication.
            email (str): Email address for the user account.
            password (str | None): Raw password to hash and store.
            **extra_fields: Additional model fields passed to the user model.

        Returns:
            User: The saved user model instance.

        Raises:
            ValueError: If `username` or `email` is missing.
        """
        if not username:
            raise ValueError('The username must be provided.')
        if not email:
            raise ValueError('The email address must be provided.')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        """Create a regular non-staff user.

        Args:
            username (str): Username for the new account.
            email (str): Email address for the new account.
            password (str | None): Raw password for the account.
            **extra_fields: Extra fields applied to the model.

        Returns:
            User: A saved user configured as a standard account.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create a superuser account with editor privileges.

        Args:
            username (str): Username for the administrator.
            email (str): Email address for the administrator.
            password (str | None): Raw password for the administrator.
            **extra_fields: Extra fields applied to the model.

        Returns:
            User: A saved superuser instance.

        Raises:
            ValueError: If the required superuser flags are not set.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'editor')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, email, password, **extra_fields)
