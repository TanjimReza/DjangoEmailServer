from rest_framework import serializers
from otphome.models import Email, BandwidthLog

class BandwidthLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandwidthLog
        fields = '__all__'

class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ['from_email', 'to_email', 'subject', 'date_time', 'profile', 'login_otp', 'household_link', 'tag']
