from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.payment_dashboard,
        name='payment_dashboard'
    ),

    path(
        'all/',
        views.payment_list,
        name='payment_list'
    ),

    path(
        'create/',
        views.payment_create,
        name='payment_create'
    ),

    path(
        '<int:pk>/',
        views.payment_detail,
        name='payment_detail'
    ),

    path(
        '<int:pk>/edit/',
        views.payment_edit,
        name='payment_edit'
    ),

    path(
        '<int:pk>/delete/',
        views.payment_delete,
        name='payment_delete'
    ),

    path(
        '<int:pk>/successful/',
        views.mark_payment_successful,
        name='mark_payment_successful'
    ),

    path(
        '<int:pk>/failed/',
        views.mark_payment_failed,
        name='mark_payment_failed'
    ),
]