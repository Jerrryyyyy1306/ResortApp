from django.urls import path

from . import views


urlpatterns = [

    # ======================================================
    # ADMIN AUTHENTICATION
    # ======================================================

    path(
        'admin-login/',
        views.admin_login,
        name='admin_login'
    ),

    path(
        'admin-logout/',
        views.admin_logout,
        name='admin_logout'
    ),

    # ======================================================
    # USER MANAGEMENT
    # ======================================================

    path(
        'admin-dashboard/users/',
        views.user_list,
        name='user_list'
    ),

    path(
        'admin-dashboard/users/add/',
        views.user_create,
        name='user_create'
    ),

    path(
        'admin-dashboard/users/<int:user_id>/',
        views.user_detail,
        name='user_detail'
    ),

    path(
        'admin-dashboard/users/<int:user_id>/edit/',
        views.user_edit,
        name='user_edit'
    ),

    path(
        'admin-dashboard/users/<int:user_id>/password/',
        views.user_change_password,
        name='user_change_password'
    ),

    path(
        'admin-dashboard/users/<int:user_id>/suspend/',
        views.user_suspend,
        name='user_suspend'
    ),

    path(
        'admin-dashboard/users/<int:user_id>/activate/',
        views.user_activate,
        name='user_activate'
    ),

    path(
        'admin-dashboard/users/<int:user_id>/delete/',
        views.user_delete,
        name='user_delete'
    ),
]