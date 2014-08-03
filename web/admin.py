from django.contrib import admin
from models import Item, Buy, UserProfile


class ItemAdmin(admin.ModelAdmin):
    list_filter = ('multi_item', 'already_given', 'surprise', 'user',)
    list_display = ('name', 'multi_item', 'already_given',)

    class Meta:
        model = Item


admin.site.register(Item, ItemAdmin)
admin.site.register(Buy)
admin.site.register(UserProfile)
