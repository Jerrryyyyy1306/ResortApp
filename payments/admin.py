from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        'payment_reference',
        'booking',
        'client',
        'amount',
        'payment_method',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'payment_method',
        'created_at',
    )

    search_fields = (
        'payment_reference',
        'transaction_id',
        'booking__booking_reference',
        'client__username',
        'client__first_name',
        'client__last_name',
    )

    readonly_fields = (
        'payment_reference',
        'created_at',
        'updated_at',
    )

    ordering = (
        '-created_at',
    )