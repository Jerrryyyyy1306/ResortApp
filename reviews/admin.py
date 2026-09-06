from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'client',
        'property',
        'rating',
        'status',
        'is_flagged',
        'created_at',
    )

    list_filter = (
        'status',
        'rating',
        'is_flagged',
        'created_at',
    )

    search_fields = (
        'title',
        'comment',
        'client__username',
        'client__first_name',
        'client__last_name',
        'property__name',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'moderated_at',
    )

    list_per_page = 25