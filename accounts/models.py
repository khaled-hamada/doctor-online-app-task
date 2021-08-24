from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import validate_email
from django.conf import settings

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_args):

        if not email:
            raise ValueError('Users must have an email address')
        ## check correct email
        try:
            validate_email(email)
        except Exception as ex:
            raise ValueError('Users must have a vaild email address')

        user = self.model(email=self.normalize_email(email), **extra_args)
        # password must be encypted before being saved
        user.set_password(password)
        user.save(using=self._db)  # allow client to use and dbms

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """ custom user model to use an email for auth. 
        instead of user name 
    
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
   
    def __str__(self):
        return self.email


class Doctor(models.Model):
    """ doctor model extends user with its cutom filed if any  """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.name 
class Patient(models.Model):
    """ Patient model extends user with its cutom filed if any  """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name