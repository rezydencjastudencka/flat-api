from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from charges.models import Charge, Flat, Profile


class UserProfileInline(admin.StackedInline):
    model = Profile
    max_num = 1
    can_delete = False


class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)

admin.site.register(Charge)
admin.site.register(Flat)
