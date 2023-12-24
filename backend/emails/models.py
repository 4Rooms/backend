from django.db import models


class EmailInfo(models.Model):
    email = models.EmailField()
    country_code = models.CharField(max_length=2, blank=True, null=True)
    is_disposable = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)


class DomainInfo(models.Model):
    domain = models.CharField(max_length=255)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    is_spam = models.BooleanField(default=False)
