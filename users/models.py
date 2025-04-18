from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class User(AbstractUser):
    #username, first_naem, last_name, email, is_staff, is,active, date_joined이 AbstractUser에 포함. 
    


    def __str__(self):
        return self.username
