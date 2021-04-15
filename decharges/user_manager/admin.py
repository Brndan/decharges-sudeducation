from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from decharges.user_manager.models import Syndicat

admin.site.register(Syndicat, UserAdmin)
