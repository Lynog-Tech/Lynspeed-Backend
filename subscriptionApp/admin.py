from django.contrib import admin
from .models import Plan, Subscription, Payment

class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration')
    search_fields = ('name',)
    list_filter = ('price',)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'status')
    search_fields = ('user__email', 'plan__name')
    list_filter = ('status', 'plan')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_date', 'transaction_id')
    search_fields = ('user__email', 'transaction_id')
    list_filter = ('amount', 'payment_date')

admin.site.register(Plan, PlanAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Payment, PaymentAdmin)
