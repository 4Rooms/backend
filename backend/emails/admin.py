from django.contrib import admin
from emails.models import DomainInfo, EmailInfo

admin.site.register(EmailInfo)
admin.site.register(DomainInfo)
