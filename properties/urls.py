from django.urls import path

from . import views


urlpatterns = [

    path(
        '',
        views.property_list,
        name='property_list'
    ),

    path(
        'add/',
        views.property_create,
        name='property_create'
    ),

    path(
        '<int:property_id>/',
        views.property_detail,
        name='property_detail'
    ),

    path(
        '<int:property_id>/edit/',
        views.property_edit,
        name='property_edit'
    ),

    path(
        '<int:property_id>/delete/',
        views.property_delete,
        name='property_delete'
    ),

    path(
        '<int:property_id>/approve/',
        views.property_approve,
        name='property_approve'
    ),

    path(
        '<int:property_id>/reject/',
        views.property_reject,
        name='property_reject'
    ),

    path(
        '<int:property_id>/suspend/',
        views.property_suspend,
        name='property_suspend'
    ),

    path(
        '<int:property_id>/activate/',
        views.property_activate,
        name='property_activate'
    ),

    path(
        '<int:property_id>/featured/',
        views.property_toggle_featured,
        name='property_toggle_featured'
    ),

    path(
        '<int:property_id>/verified/',
        views.property_toggle_verified,
        name='property_toggle_verified'
    ),

    path(
        '<int:property_id>/rooms/add/',
        views.room_create,
        name='room_create'
    ),

    path(
        'rooms/<int:room_id>/edit/',
        views.room_edit,
        name='room_edit'
    ),

    path(
        'rooms/<int:room_id>/delete/',
        views.room_delete,
        name='room_delete'
    ),

    path(
        '<int:property_id>/images/add/',
        views.image_create,
        name='image_create'
    ),

    path(
        'images/<int:image_id>/delete/',
        views.image_delete,
        name='image_delete'
    ),

        # Amenities
    path(
        'amenities/',
        views.amenity_list,
        name='amenity_list'
    ),

    path(
        'amenities/add/',
        views.amenity_create,
        name='amenity_create'
    ),

    path(
        'amenities/<int:amenity_id>/edit/',
        views.amenity_edit,
        name='amenity_edit'
    ),

    path(
        'amenities/<int:amenity_id>/delete/',
        views.amenity_delete,
        name='amenity_delete'
    ),

    path(
        'amenities/<int:amenity_id>/toggle-status/',
        views.amenity_toggle_status,
        name='amenity_toggle_status'
    ),

]