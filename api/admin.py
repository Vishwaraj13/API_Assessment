from django.contrib import admin

from api.models import transaction,company,average_buy
# Register your models here.

admin.site.register(transaction)
admin.site.register(company)
admin.site.register(average_buy)