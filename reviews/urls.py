from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.review_dashboard,
        name='review_dashboard'
    ),

    path(
        'all/',
        views.review_list,
        name='review_list'
    ),

    path(
        'create/',
        views.review_create,
        name='review_create'
    ),

    path(
        '<int:pk>/',
        views.review_detail,
        name='review_detail'
    ),

    path(
        '<int:pk>/edit/',
        views.review_edit,
        name='review_edit'
    ),

    path(
        '<int:pk>/delete/',
        views.review_delete,
        name='review_delete'
    ),

    path(
        '<int:pk>/approve/',
        views.approve_review,
        name='approve_review'
    ),

    path(
        '<int:pk>/reject/',
        views.reject_review,
        name='reject_review'
    ),

    path(
        '<int:pk>/flag/',
        views.toggle_flag_review,
        name='toggle_flag_review'
    ),
]