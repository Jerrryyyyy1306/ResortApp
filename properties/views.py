from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.core.paginator import Paginator

from accounts.views import is_admin
from accounts.views import is_super_admin

from .forms import PropertyForm
from .forms import PropertyImageForm
from .forms import RoomForm
from .models import Property
from .models import PropertyImage
from .models import Room

from .models import Amenity
from .models import Property
from .models import PropertyImage
from .models import Room

from .forms import PropertyForm
from .forms import PropertyImageForm
from .forms import RoomForm
from .forms import AmenityForm


# ==========================================================
# PROPERTY LIST
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def property_list(request):

    properties = Property.objects.select_related(
        'owner'
    ).prefetch_related(
        'amenities'
    ).all()

    # ------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------

    search = request.GET.get(
        'search',
        ''
    ).strip()

    if search:

        properties = properties.filter(

            Q(name__icontains=search)
            |
            Q(city__icontains=search)
            |
            Q(province__icontains=search)
            |
            Q(owner__username__icontains=search)
            |
            Q(owner__email__icontains=search)

        )

    # ------------------------------------------------------
    # PROPERTY TYPE
    # ------------------------------------------------------

    property_type = request.GET.get(
        'property_type',
        ''
    )

    if property_type:

        properties = properties.filter(
            property_type=property_type
        )

    # ------------------------------------------------------
    # STATUS
    # ------------------------------------------------------

    status = request.GET.get(
        'status',
        ''
    )

    if status:

        properties = properties.filter(
            status=status
        )

    # ------------------------------------------------------
    # FEATURED
    # ------------------------------------------------------

    featured = request.GET.get(
        'featured',
        ''
    )

    if featured == 'yes':

        properties = properties.filter(
            is_featured=True
        )

    elif featured == 'no':

        properties = properties.filter(
            is_featured=False
        )

    # ------------------------------------------------------
    # VERIFIED
    # ------------------------------------------------------

    verified = request.GET.get(
        'verified',
        ''
    )

    if verified == 'yes':

        properties = properties.filter(
            is_verified=True
        )

    elif verified == 'no':

        properties = properties.filter(
            is_verified=False
        )

    # ------------------------------------------------------
    # PAGINATION
    # ------------------------------------------------------

    paginator = Paginator(
        properties,
        15
    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )

    # ------------------------------------------------------
    # STATISTICS
    # ------------------------------------------------------

    context = {

        'page_obj': page_obj,

        'search': search,

        'selected_type': property_type,

        'selected_status': status,

        'selected_featured': featured,

        'selected_verified': verified,

        'total_properties':
            Property.objects.count(),

        'pending_properties':
            Property.objects.filter(
                status='pending'
            ).count(),

        'approved_properties':
            Property.objects.filter(
                status='approved'
            ).count(),

        'rejected_properties':
            Property.objects.filter(
                status='rejected'
            ).count(),

        'suspended_properties':
            Property.objects.filter(
                status='suspended'
            ).count(),

        'featured_properties':
            Property.objects.filter(
                is_featured=True
            ).count(),

    }

    return render(
        request,
        'dashboard/properties/property_list.html',
        context
    )


# ==========================================================
# CREATE
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def property_create(request):

    if request.method == 'POST':

        form = PropertyForm(
            request.POST
        )

        if form.is_valid():

            property_obj = form.save()

            messages.success(
                request,
                f'Property "{property_obj.name}" was created successfully.'
            )

            return redirect(
                'property_detail',
                property_id=property_obj.id
            )

    else:

        form = PropertyForm()

    return render(
        request,
        'dashboard/properties/property_form.html',
        {
            'form': form,
            'page_title': 'Add Property',
            'button_text': 'Create Property',
        }
    )


# ==========================================================
# DETAIL
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def property_detail(
    request,
    property_id
):

    property_obj = get_object_or_404(
        Property.objects.select_related(
            'owner'
        ).prefetch_related(
            'amenities',
            'images',
            'rooms'
        ),
        id=property_id
    )

    return render(
        request,
        'dashboard/properties/property_detail.html',
        {
            'property_obj': property_obj
        }
    )


# ==========================================================
# EDIT
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def property_edit(
    request,
    property_id
):

    property_obj = get_object_or_404(
        Property,
        id=property_id
    )

    if request.method == 'POST':

        form = PropertyForm(
            request.POST,
            instance=property_obj
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                f'Property "{property_obj.name}" was updated successfully.'
            )

            return redirect(
                'property_detail',
                property_id=property_obj.id
            )

    else:

        form = PropertyForm(
            instance=property_obj
        )

    return render(
        request,
        'dashboard/properties/property_form.html',
        {
            'form': form,
            'page_title': f'Edit {property_obj.name}',
            'button_text': 'Save Changes',
            'property_obj': property_obj,
        }
    )


# ==========================================================
# DELETE
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def property_delete(
    request,
    property_id
):

    property_obj = get_object_or_404(
        Property,
        id=property_id
    )

    if request.method == 'POST':

        name = property_obj.name

        property_obj.delete()

        messages.success(
            request,
            f'Property "{name}" was deleted successfully.'
        )

        return redirect(
            'property_list'
        )

    return render(
        request,
        'dashboard/properties/confirm_delete.html',
        {
            'property_obj': property_obj
        }
    )


# ==========================================================
# APPROVE
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def property_approve(
    request,
    property_id
):

    property_obj = get_object_or_404(
        Property,
        id=property_id
    )

    if request.method == 'POST':

        property_obj.status = 'approved'

        property_obj.is_active = True

        property_obj.approved_at = timezone.now()

        property_obj.rejection_reason = ''

        property_obj.save()

        messages.success(
            request,
            f'"{property_obj.name}" has been approved.'
        )

    return redirect(
        'property_detail',
        property_id=property_obj.id
    )


# ==========================================================
# REJECT
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def property_reject(
    request,
    property_id
):

    property_obj = get_object_or_404(
        Property,
        id=property_id
    )

    if request.method == 'POST':

        reason = request.POST.get(
            'reason',
            ''
        ).strip()

        property_obj.status = 'rejected'

        property_obj.rejection_reason = reason

        property_obj.is_active = False

        property_obj.save()

        messages.success(
            request,
            f'"{property_obj.name}" has been rejected.'
        )

    return redirect(
        'property_detail',
        property_id=property_obj.id
    )


# ==========================================================
# SUSPEND
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def property_suspend(
    request,
    property_id
):

    property_obj = get_object_or_404(
        Property,
        id=property_id
    )

    if request.method == 'POST':

        reason = request.POST.get(
            'reason',
            ''
        ).strip()

        property_obj.status = 'suspended'

        property_obj.suspension_reason = reason

        property_obj.is_active = False

        property_obj.save()

        messages.success(
            request,
            f'"{property_obj.name}" has been suspended.'
        )

    return redirect(
        'property_detail',
        property_id=property_obj.id
    )


# ==========================================================
# ACTIVATE
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def property_activate(
    request,
    property_id
):

    property_obj = get_object_or_404(
        Property,
        id=property_id
    )

    if request.method == 'POST':

        property_obj.status = 'approved'

        property_obj.is_active = True

        property_obj.suspension_reason = ''

        property_obj.save()

        messages.success(
            request,
            f'"{property_obj.name}" has been activated.'
        )

    return redirect(
        'property_detail',
        property_id=property_obj.id
    )


# ==========================================================
# FEATURE / UNFEATURE
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def property_toggle_featured(
    request,
    property_id
):

    property_obj = get_object_or_404(
        Property,
        id=property_id
    )

    if request.method == 'POST':

        property_obj.is_featured = not property_obj.is_featured

        property_obj.save(
            update_fields=[
                'is_featured',
                'updated_at'
            ]
        )

    return redirect(
        'property_detail',
        property_id=property_obj.id
    )


# ==========================================================
# VERIFY / UNVERIFY
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def property_toggle_verified(
    request,
    property_id
):

    property_obj = get_object_or_404(
        Property,
        id=property_id
    )

    if request.method == 'POST':

        property_obj.is_verified = not property_obj.is_verified

        property_obj.save(
            update_fields=[
                'is_verified',
                'updated_at'
            ]
        )

    return redirect(
        'property_detail',
        property_id=property_obj.id
    )


# ==========================================================
# ADD ROOM
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def room_create(
    request,
    property_id
):

    property_obj = get_object_or_404(
        Property,
        id=property_id
    )

    if request.method == 'POST':

        form = RoomForm(
            request.POST
        )

        if form.is_valid():

            room = form.save(
                commit=False
            )

            room.property = property_obj

            room.save()

            messages.success(
                request,
                f'Room "{room.name}" was added.'
            )

            return redirect(
                'property_detail',
                property_id=property_obj.id
            )

    else:

        form = RoomForm()

    return render(
        request,
        'dashboard/properties/room_form.html',
        {
            'form': form,
            'property_obj': property_obj,
            'page_title': 'Add Room',
        }
    )


# ==========================================================
# EDIT ROOM
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def room_edit(
    request,
    room_id
):

    room = get_object_or_404(
        Room,
        id=room_id
    )

    if request.method == 'POST':

        form = RoomForm(
            request.POST,
            instance=room
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                f'Room "{room.name}" was updated.'
            )

            return redirect(
                'property_detail',
                property_id=room.property.id
            )

    else:

        form = RoomForm(
            instance=room
        )

    return render(
        request,
        'dashboard/properties/room_form.html',
        {
            'form': form,
            'property_obj': room.property,
            'room': room,
            'page_title': f'Edit Room: {room.name}',
        }
    )


# ==========================================================
# DELETE ROOM
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def room_delete(
    request,
    room_id
):

    room = get_object_or_404(
        Room,
        id=room_id
    )

    property_id = room.property.id

    if request.method == 'POST':

        room.delete()

        messages.success(
            request,
            'Room deleted successfully.'
        )

        return redirect(
            'property_detail',
            property_id=property_id
        )

    return render(
        request,
        'dashboard/properties/confirm_room_delete.html',
        {
            'room': room
        }
    )


# ==========================================================
# ADD IMAGE
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def image_create(
    request,
    property_id
):

    property_obj = get_object_or_404(
        Property,
        id=property_id
    )

    if request.method == 'POST':

        form = PropertyImageForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            image = form.save(
                commit=False
            )

            image.property = property_obj

            image.save()

            messages.success(
                request,
                'Property image uploaded successfully.'
            )

            return redirect(
                'property_detail',
                property_id=property_obj.id
            )

    else:

        form = PropertyImageForm()

    return render(
        request,
        'dashboard/properties/image_form.html',
        {
            'form': form,
            'property_obj': property_obj,
        }
    )


# ==========================================================
# DELETE IMAGE
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def image_delete(
    request,
    image_id
):

    image = get_object_or_404(
        PropertyImage,
        id=image_id
    )

    property_id = image.property.id

    if request.method == 'POST':

        image.delete()

        messages.success(
            request,
            'Property image deleted.'
        )

    return redirect(
        'property_detail',
        property_id=property_id
    )

# ==========================================================
# AMENITIES MANAGEMENT
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def amenity_list(request):

    amenities = Amenity.objects.all()

    search = request.GET.get(
        'search',
        ''
    ).strip()

    status = request.GET.get(
        'status',
        ''
    )

    # Search
    if search:

        amenities = amenities.filter(
            Q(name__icontains=search)
            |
            Q(description__icontains=search)
        )

    # Status filter
    if status == 'active':

        amenities = amenities.filter(
            is_active=True
        )

    elif status == 'inactive':

        amenities = amenities.filter(
            is_active=False
        )

    # Statistics
    total_amenities = Amenity.objects.count()

    active_amenities = Amenity.objects.filter(
        is_active=True
    ).count()

    inactive_amenities = Amenity.objects.filter(
        is_active=False
    ).count()

    # Properties using amenities
    for amenity in amenities:

        amenity.property_count = amenity.properties.count()

    context = {

        'amenities': amenities,

        'search': search,

        'selected_status': status,

        'total_amenities': total_amenities,

        'active_amenities': active_amenities,

        'inactive_amenities': inactive_amenities,

    }

    return render(
        request,
        'dashboard/properties/amenities/amenity_list.html',
        context
    )


# ==========================================================
# CREATE AMENITY
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def amenity_create(request):

    if request.method == 'POST':

        form = AmenityForm(
            request.POST
        )

        if form.is_valid():

            amenity = form.save()

            messages.success(
                request,
                f'Amenity "{amenity.name}" was created successfully.'
            )

            return redirect(
                'amenity_list'
            )

    else:

        form = AmenityForm()

    return render(
        request,
        'dashboard/properties/amenities/amenity_form.html',
        {
            'form': form,
            'page_title': 'Add Amenity',
            'button_text': 'Create Amenity',
        }
    )


# ==========================================================
# EDIT AMENITY
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def amenity_edit(
    request,
    amenity_id
):

    amenity = get_object_or_404(
        Amenity,
        id=amenity_id
    )

    if request.method == 'POST':

        form = AmenityForm(
            request.POST,
            instance=amenity
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                f'Amenity "{amenity.name}" was updated successfully.'
            )

            return redirect(
                'amenity_list'
            )

    else:

        form = AmenityForm(
            instance=amenity
        )

    return render(
        request,
        'dashboard/properties/amenities/amenity_form.html',
        {
            'form': form,
            'page_title': f'Edit Amenity: {amenity.name}',
            'button_text': 'Save Changes',
            'amenity': amenity,
        }
    )


# ==========================================================
# DELETE AMENITY
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def amenity_delete(
    request,
    amenity_id
):

    amenity = get_object_or_404(
        Amenity,
        id=amenity_id
    )

    if request.method == 'POST':

        name = amenity.name

        amenity.delete()

        messages.success(
            request,
            f'Amenity "{name}" was deleted successfully.'
        )

        return redirect(
            'amenity_list'
        )

    return render(
        request,
        'dashboard/properties/amenities/amenity_confirm_delete.html',
        {
            'amenity': amenity
        }
    )


# ==========================================================
# ACTIVATE / DEACTIVATE
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def amenity_toggle_status(
    request,
    amenity_id
):

    amenity = get_object_or_404(
        Amenity,
        id=amenity_id
    )

    if request.method == 'POST':

        amenity.is_active = not amenity.is_active

        amenity.save(
            update_fields=[
                'is_active'
            ]
        )

        if amenity.is_active:

            messages.success(
                request,
                f'"{amenity.name}" has been activated.'
            )

        else:

            messages.success(
                request,
                f'"{amenity.name}" has been deactivated.'
            )

    return redirect(
        'amenity_list'
    )