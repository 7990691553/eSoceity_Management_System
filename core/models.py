from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            # You can also choose to raise error instead of allowing empty password
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    One user model for the whole project (common auth).
    Login is by email + password.
    """

    ROLE_CHOICES = (
        ("super_admin", "Super Admin"),
        ("chairman", "Admin/Chairman"),
        ("member", "Society Member"),
        ("security", "Security Person"),
        ("helper", "House Helper"),
    )

    # --- Login / identity ---
    email = models.EmailField(unique=True)

    # --- Basic profile (common for all humans using system) ---
    full_name = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=15, unique=True)

    # --- Role / access control ---
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")

    # --- Admin flags ---
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # can access /admin if True

    # --- timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "contact_no"]

    def __str__(self):
        return self.email
