from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from .choice import PermissionModule


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Role(TimeStampedModel):
    role_name = models.CharField(max_length=255, unique=True)
    company = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return self.role_name


class RolePermission(TimeStampedModel):
    """What a role may do in one module."""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    module = models.CharField(max_length=50, choices=PermissionModule.choices)
    submodule = models.CharField(max_length=50, blank=True, default='')
    can_view = models.BooleanField(default=False)    # GET / HEAD / OPTIONS
    can_add = models.BooleanField(default=False)     # POST
    can_change = models.BooleanField(default=False)  # PUT / PATCH
    can_delete = models.BooleanField(default=False)  # DELETE

    class Meta:
        unique_together = ('role', 'module', 'submodule')

    def __str__(self):
        flags = ''.join(
            flag for flag, allowed in
            (('v', self.can_view), ('a', self.can_add), ('c', self.can_change), ('d', self.can_delete))
            if allowed
        )
        target = f'{self.module}.{self.submodule}' if self.submodule else self.module
        return f'{target}: {flags or "-"}'


class UserManager(BaseUserManager):
    def create_user(self, email=None, name='', password=None, phone=None, **extra_fields):
        if not email and not phone:
            raise ValueError('Users must provide an email address or mobile number.')
        email = self.normalize_email(email) if email else None
        user = self.model(email=email, name=name, phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create(self, password=None, **extra_fields):
        return self.create_user(password=password, **extra_fields)

    def create_superuser(self, email, name='Admin', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email=email, name=name, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    name = models.CharField(max_length=255, blank=True, default='')
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='users', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def save(self, *args, **kwargs):
        if not self.name and (self.first_name or self.last_name):
            self.name = f'{self.first_name} {self.last_name}'.strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.phone or str(self.pk)


class Address(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True, default='')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.full_name} ({self.city}, {self.pincode})'


class OtpCode(TimeStampedModel):
    phone = models.CharField(max_length=20, db_index=True)
    otp = models.CharField(max_length=10)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f'OTP for {self.phone}'
