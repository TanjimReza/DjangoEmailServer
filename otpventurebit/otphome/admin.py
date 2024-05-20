from django.contrib import admin
from .models import Email, BandwidthLog
# Register your models here.
admin.site.register(Email)
admin.site.register(BandwidthLog)