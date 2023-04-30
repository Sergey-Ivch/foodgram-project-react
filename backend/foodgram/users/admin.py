from django.contrib import admin
from .models import Buyer


class BuyerAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'pk', 'email', 'password', 'first_name', 'last_name',
    )
    list_editable = ('password',)
    list_filter = ('username',)
    search_fields = ('username',)
    empty_value_display = '-пусто-'

admin.site.register(Buyer, BuyerAdmin) 

