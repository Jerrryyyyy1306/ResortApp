from django.urls import path

from . import views


urlpatterns = [

    path(
        '',
        views.booking_dashboard,
        name='booking_dashboard'
    ),

    path(
        'all/',
        views.booking_list,
        name='booking_list'
    ),

    path(
        'create/',
        views.booking_create,
        name='booking_create'
    ),

    path(
        '<int:booking_id>/',
        views.booking_detail,
        name='booking_detail'
    ),

    path(
        '<int:booking_id>/edit/',
        views.booking_edit,
        name='booking_edit'
    ),

    path(
        '<int:booking_id>/confirm/',
        views.booking_confirm,
        name='booking_confirm'
    ),

    path(
        '<int:booking_id>/check-in/',
        views.booking_check_in,
        name='booking_check_in'
    ),

    path(
        '<int:booking_id>/complete/',
        views.booking_complete,
        name='booking_complete'
    ),

    path(
        '<int:booking_id>/cancel/',
        views.booking_cancel,
        name='booking_cancel'
    ),

    path(
        '<int:booking_id>/reject/',
        views.booking_reject,
        name='booking_reject'
    ),

    path(
        '<int:booking_id>/payment/',
        views.booking_payment,
        name='booking_payment'
    ),
]