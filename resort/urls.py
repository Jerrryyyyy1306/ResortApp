from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from django.urls import path
from django.urls import path, include


urlpatterns = [

    # Client Side

    path(
        'account/',
        include('accounts.client_urls')
    ),

    #Admin Side

    path(
        'django-admin/',
        admin.site.urls
    ),

    path(
        '',
        include('accounts.urls')
    ),

    path(
        'admin-dashboard/',
        include('dashboard.urls')
    ),

    path(
        'admin-dashboard/properties/',
        include('properties.urls')
    ),

    path(
        'admin-dashboard/bookings/',
        include('bookings.urls')
    ),

    path(
        'admin-dashboard/payments/',
        include('payments.urls')
    ),

    path(
        'admin-dashboard/reviews/',
        include('reviews.urls')
    ),
]


if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )