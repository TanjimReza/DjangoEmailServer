from datetime import datetime

from django.db import models
from django.utils.timezone import get_default_timezone, is_aware, make_aware


# Create your models here.
class Email(models.Model):
    id = models.AutoField(primary_key=True)
    from_email = models.EmailField(
        max_length=254, blank=True, null=True, db_index=True)
    to_email = models.EmailField(max_length=254, blank=True, null=True)
    subject = models.CharField(max_length=254, blank=True, null=True)
    body = models.TextField(blank=True, null=True)

    date_time = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    profile = models.CharField(
        max_length=254, blank=True, null=True, db_index=True)
    login_otp = models.CharField(max_length=254, blank=True, null=True)
    household_link = models.CharField(max_length=254, blank=True, null=True)

    tag = models.CharField(max_length=254, blank=True,
                           null=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if isinstance(self.date_time, str):
            # Parse the date-time string to a datetime object
            parsed_date_time = datetime.strptime(
                self.date_time, '%Y-%m-%d %H:%M:%S')
            # Make the datetime object timezone aware if it is not already
            if not is_aware(parsed_date_time):
                parsed_date_time = make_aware(
                    parsed_date_time, get_default_timezone())
            self.date_time = parsed_date_time

        super().save(*args, **kwargs)

    @classmethod
    def get_most_recent_emails_by_tag_and_profile(cls, profile, tag, count=3):
        return cls.objects.filter(profile=profile, tag=tag).order_by('-date_time')[:count]

    @classmethod
    def get_most_recent_emails_by_tag_and_email(cls, email, tag, count=3):
        return cls.objects.filter(to_email=email, tag=tag).order_by('-date_time')[:count]

    def __str__(self):
        return f"F:{self.from_email} - T:{self.to_email} - Tag:{self.tag} - Profile:{self.profile}"
    # def get_most_recent_otp_emails(account_email, count=3):
    #     recent_emails = Email.objects.filter(to_email=account_email, tag="LOGIN").order_by('-date_time')[:count]
    #     return list(recent_emails) + [None] * (count - len(recent_emails))

    # def get_most_recent_household_emails(account_email, count=3):
    #     recent_emails = Email.objects.filter(to_email=account_email, tag="HOUSEHOLD").order_by('-date_time')[:count]
    #     return list(recent_emails) + [None] * (count - len(recent_emails))

    # def __str__(self):
    #     return f"F:{self.from_email} - T:{self.to_email} - T:{self.tag}"
