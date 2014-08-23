from django.contrib import admin
from models import Item, Buy, UserProfile, Occasion


class ItemAdmin(admin.ModelAdmin):
    list_filter = ('multi_item', 'already_given', 'surprise', 'user',)
    list_display = ('name', 'multi_item', 'already_given',)

    class Meta:
        model = Item


class OccasionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'month', 'day',)

    class Meta:
        model = Occasion


admin.site.register(Item, ItemAdmin)
admin.site.register(Buy)
admin.site.register(UserProfile)
admin.site.register(Occasion, OccasionAdmin)
