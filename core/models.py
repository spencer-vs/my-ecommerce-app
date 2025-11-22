from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group

# Create your models here.
class CustomUser(AbstractUser):
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
   
    groups = models.ManyToManyField(
        'auth.Group',  # Correct reference to auth.Group
        verbose_name='custom_user_groups',
        blank=True,
        help_text='The groups the user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='customuser_groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',  # Correct reference to auth.Permission
        verbose_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_permissions',
    )
    def __str__(self):
        return self.username
    
    
    def save(self, *args, **kwargs):
        if self.pk is None:                    # ← NEW: only on create
            self.is_active = True
        super().save(*args, **kwargs)
        from django.contrib.auth.models import Group
        customer, _ = Group.objects.get_or_create(name='Customer')
        if not self.groups.filter(name='Customer').exists():
            self.groups.add(customer)