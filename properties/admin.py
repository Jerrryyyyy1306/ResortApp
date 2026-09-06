from django.contrib import admin

from .models import Amenity
from .models import Property
from .models import PropertyImage
from .models import Room


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'is_active',
        'created_at',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'name',
    )


class PropertyImageInline(admin.TabularInline):

    model = PropertyImage

    extra = 1


class RoomInline(admin.TabularInline):

    model = Room

    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'property_type',
        'owner',
        'city',
        'status',
        'is_verified',
        'is_featured',
        'created_at',
    )

    list_filter = (
        'property_type',
        'status',
        'is_verified',
        'is_featured',
        'is_active',
        'city',
    )

    search_fields = (
        'name',
        'city',
        'province',
        'owner__username',
        'owner__email',
    )

    filter_horizontal = (
        'amenities',
    )

    readonly_fields = (
        'average_rating',
        'total_reviews',
        'created_at',
        'updated_at',
        'approved_at',
    )

    inlines = [
        PropertyImageInline,
        RoomInline,
    ]

    list_per_page = 20


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):

    list_display = (
        'property',
        'caption',
        'is_primary',
        'display_order',
        'uploaded_at',
    )

    list_filter = (
        'is_primary',
    )

    search_fields = (
        'property__name',
        'caption',
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'property',
        'price_per_night',
        'max_guests',
        'quantity',
        'is_available',
    )

    list_filter = (
        'is_available',
    )

    search_fields = (
        'name',
        'property__name',
    )