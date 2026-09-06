from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path(
        'login/',
        views.client_login,
        name='account_login'
    ),

    path(
        'register/',
        views.client_register,
        name='account_register'
    ),

    path(
        'logout/',
        views.client_logout,
        name='account_logout'
    ),

    # Client dashboard
    path(
        'dashboard/',
        views.client_dashboard,
        name='client_dashboard'
    ),

    # Client account
    path(
        'profile/',
        views.client_profile,
        name='client_profile'
    ),

    path(
        'password/change/',
        views.client_password_change,
        name='client_password_change'
    ),

    # Client bookings
    path(
        'bookings/',
        views.client_bookings,
        name='client_bookings'
    ),

    path(
        'bookings/<int:booking_id>/',
        views.client_booking_detail,
        name='client_booking_detail'
    ),

    # Property details
    path(
        'properties/<int:property_id>/',
        views.client_property_detail,
        name='client_property_detail'
    ),
]