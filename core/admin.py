from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# HIDE the default "auth.User" forever
# admin.site.unregister(auth_models.User)



    

# SHOW ONLY your CustomUser under CORE
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
       fieldsets = UserAdmin.fieldsets + (
           ("Extra Info", {
               "fields": (
                   "city", "state", "address", "phone"
               ),
           }),
       )
       
    











# from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser
# from django.contrib.auth import get_user_model


# # Register your models here.

# class CustomUserAdmin(UserAdmin):
#     add_fieldsets = (
#         (None, {
#             "classes": ('wide',),
#             "fields": (
#                 'username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'city', 'state', 'address', 'phone', 'is_staff', 'is_active'
#             ),
#         }),
#     )
    
    
    

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     pass
   
    
