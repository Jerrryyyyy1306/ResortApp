from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from .forms import AdminPasswordChangeForm
from .forms import AdminUserCreateForm
from .forms import AdminUserEditForm
from .models import Profile

from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

from .forms import ClientLoginForm
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone

from properties.models import Property, PropertyImage, Room
from bookings.models import Booking

from .forms import (
    ClientLoginForm,
    ClientRegistrationForm,
)

#Client Booking Details

@login_required(login_url='account_login')
def client_booking_detail(request, booking_id):
    # Keep admin users on the admin dashboard
    if request.user.is_staff:
        return redirect('admin_dashboard')

    booking = get_object_or_404(
        Booking.objects.select_related(
            'property',
            'room'
        ).prefetch_related(
            'property__images',
            'property__amenities'
        ),
        id=booking_id,
        client=request.user
    )

    return render(
        request,
        'client/booking_detail.html',
        {
            'booking': booking,
            'user': request.user,
        }
    )

#Client Property Details

@login_required(login_url='account_login')
def client_property_detail(request, property_id):

    if request.user.is_staff:
        return redirect('admin_dashboard')

    property_obj = get_object_or_404(
        Property.objects.prefetch_related(
            'images',
            'rooms',
            'amenities'
        ),
        id=property_id,
        status='approved',
        is_active=True
    )

    return render(
        request,
        'client/property_detail.html',
        {
            'property': property_obj,
            'user': request.user,
        }
    )


#Client Bookings

@login_required(login_url='account_login')
def client_bookings(request):

    if request.user.is_staff:
        return redirect('admin_dashboard')

    bookings = Booking.objects.filter(
        client=request.user
    ).select_related(
        'property',
        'room'
    ).prefetch_related(
        'property__images'
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'client/bookings.html',
        {
            'bookings': bookings,
            'user': request.user,
        }
    )

# ============================================================
# CLIENT / PROPERTY OWNER REGISTRATION
# ============================================================

def client_register(request):

    # If already logged in, don't show registration again
    if request.user.is_authenticated:

        if request.user.is_staff:
            return redirect('admin_dashboard')

        return redirect('client_dashboard')

    if request.method == 'POST':

        form = ClientRegistrationForm(
            request.POST
        )

        if form.is_valid():

            user = form.save()

            account_type = form.cleaned_data[
                'account_type'
            ]

            # Different welcome messages depending
            # on the selected account type
            if account_type == 'owner':

                messages.success(
                    request,
                    'Your Property Owner account has been created successfully.'
                )

            else:

                messages.success(
                    request,
                    'Your Client account has been created successfully.'
                )

            # Automatically log the new user in
            login(
                request,
                user
            )

            return redirect(
                'client_dashboard'
            )

    else:

        form = ClientRegistrationForm()

    return render(
        request,
        'client/auth/register.html',
        {
            'form': form,
        }
    )



# ============================================================
# CLIENT LOGIN
# ============================================================

def client_login(request):

    # If the user is already logged in
    if request.user.is_authenticated:

        # Staff/admin users belong on the admin side
        if request.user.is_staff:
            return redirect('admin_dashboard')

        # Normal clients go to the client dashboard
        return redirect('client_dashboard')

    # Handle login form submission
    if request.method == 'POST':

        form = ClientLoginForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            # Prevent staff/admin accounts from logging
            # into the client area
            if user.is_staff:

                messages.error(
                    request,
                    'Please use the administrator login.'
                )

                return redirect('account_login')

            # Log the client in
            login(request, user)

            messages.success(
                request,
                f'Welcome back, {user.first_name or user.username}!'
            )

            return redirect('client_dashboard')

    else:

        form = ClientLoginForm()

    return render(
        request,
        'client/auth/login.html',
        {
            'form': form,
        }
    )

# ============================================================
# CLIENT DASHBOARD
# ============================================================

@login_required(login_url='account_login')
def client_dashboard(request):

    # Admins belong on the admin dashboard
    if request.user.is_staff:
        return redirect('admin_dashboard')

    user = request.user
    today = date.today()

    # =========================================================
    # SEARCH PARAMETERS
    # =========================================================

    search_query = request.GET.get('q', '').strip()

    location_query = request.GET.get(
        'location',
        ''
    ).strip()

    check_in = request.GET.get(
        'check_in',
        ''
    ).strip()

    check_out = request.GET.get(
        'check_out',
        ''
    ).strip()

    guests = request.GET.get(
        'guests',
        ''
    ).strip()

    property_type = request.GET.get(
        'property_type',
        ''
    ).strip()

    # =========================================================
    # PROPERTY QUERY
    # =========================================================

    property_queryset = Property.objects.filter(
        status='approved',
        is_active=True
    )

    # Search bar
    if search_query:
        property_queryset = property_queryset.filter(
            Q(name__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(country__icontains=search_query)
        )

    # Destination search
    if location_query:
        property_queryset = property_queryset.filter(
            Q(city__icontains=location_query) |
            Q(address__icontains=location_query) |
            Q(province__icontains=location_query) |
            Q(country__icontains=location_query)
        )

    # Property type
    if property_type in [
        'resort',
        'lodge',
        'guest_house'
    ]:
        property_queryset = property_queryset.filter(
            property_type=property_type
        )

    # Guest capacity
    if guests.isdigit():

        guest_count = int(guests)

        if guest_count > 0:
            property_queryset = property_queryset.filter(
                rooms__is_available=True,
                rooms__max_guests__gte=guest_count
            ).distinct()

    # =========================================================
    # PREFETCH
    # =========================================================

    primary_images = PropertyImage.objects.filter(
        is_primary=True
    ).order_by(
        'display_order',
        '-uploaded_at'
    )

    available_rooms = Room.objects.filter(
        is_available=True
    ).order_by(
        'price_per_night'
    )

    property_queryset = property_queryset.prefetch_related(
        Prefetch(
            'images',
            queryset=primary_images,
            to_attr='primary_images'
        ),
        Prefetch(
            'rooms',
            queryset=available_rooms,
            to_attr='available_rooms'
        ),
        'amenities'
    )

    # =========================================================
    # PROPERTY SECTIONS
    # =========================================================

    search_results = property_queryset[:12]

    has_search = any([
        search_query,
        location_query,
        check_in,
        check_out,
        guests,
        property_type
    ])

    featured_properties = Property.objects.filter(
        status='approved',
        is_active=True,
        is_featured=True
    ).prefetch_related(
        Prefetch(
            'images',
            queryset=primary_images,
            to_attr='primary_images'
        ),
        Prefetch(
            'rooms',
            queryset=available_rooms,
            to_attr='available_rooms'
        ),
        'amenities'
    )[:6]

    top_rated_properties = Property.objects.filter(
        status='approved',
        is_active=True,
        average_rating__gt=0
    ).prefetch_related(
        Prefetch(
            'images',
            queryset=primary_images,
            to_attr='primary_images'
        ),
        Prefetch(
            'rooms',
            queryset=available_rooms,
            to_attr='available_rooms'
        ),
        'amenities'
    ).order_by(
        '-average_rating',
        '-total_reviews'
    )[:6]

    # =========================================================
    # BOOKINGS
    # =========================================================

    user_bookings = Booking.objects.filter(
        client=user
    ).select_related(
        'property',
        'room'
    ).prefetch_related(
        Prefetch(
            'property__images',
            queryset=primary_images,
            to_attr='primary_images'
        )
    )

    upcoming_bookings = user_bookings.filter(
        check_out__gte=today
    ).exclude(
        status__in=[
            'cancelled',
            'rejected'
        ]
    ).order_by(
        'check_in'
    )[:5]

    recent_bookings = user_bookings.order_by(
        '-created_at'
    )[:5]

    # =========================================================
    # BOOKING COUNTS
    # =========================================================

    total_bookings = user_bookings.count()

    confirmed_bookings = user_bookings.filter(
        status='confirmed'
    ).count()

    pending_bookings = user_bookings.filter(
        status='pending'
    ).count()

    completed_bookings = user_bookings.filter(
        status='completed'
    ).count()

    cancelled_bookings = user_bookings.filter(
        status='cancelled'
    ).count()

    active_bookings = user_bookings.filter(
        status__in=[
            'pending',
            'confirmed',
            'checked_in'
        ]
    ).count()

    # =========================================================
    # PROPERTY COUNTS
    # =========================================================

    approved_properties = Property.objects.filter(
        status='approved',
        is_active=True
    )

    resort_count = approved_properties.filter(
        property_type='resort'
    ).count()

    lodge_count = approved_properties.filter(
        property_type='lodge'
    ).count()

    guest_house_count = approved_properties.filter(
        property_type='guest_house'
    ).count()

    # =========================================================
    # USER INFORMATION
    # =========================================================

    first_name = user.first_name or user.username

    context = {
        'user': user,

        'first_name': first_name,

        # Search
        'search_query': search_query,
        'location_query': location_query,
        'check_in': check_in,
        'check_out': check_out,
        'guests': guests,
        'property_type': property_type,
        'has_search': has_search,

        # Properties
        'search_results': search_results,
        'featured_properties': featured_properties,
        'top_rated_properties': top_rated_properties,

        'resort_count': resort_count,
        'lodge_count': lodge_count,
        'guest_house_count': guest_house_count,

        # Bookings
        'upcoming_bookings': upcoming_bookings,
        'recent_bookings': recent_bookings,

        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
        'completed_bookings': completed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'active_bookings': active_bookings,

        # Date
        'today': today,
    }

    return render(
        request,
        'client/dashboard.html',
        context
    )

# ============================================================
# CLIENT LOGOUT
# ============================================================

def client_logout(request):

    # Log the user out
    logout(request)

    messages.success(
        request,
        'You have been logged out successfully.'
    )

    return redirect('account_login')


# ============================================================
# CLIENT PROFILE
# ============================================================

def client_profile(request):

    # Client must be logged in
    if not request.user.is_authenticated:
        return redirect('account_login')

    # Staff/admin users should remain on admin side
    if request.user.is_staff:
        return redirect('admin_dashboard')

    return render(
        request,
        'client/profile.html'
    )


# ============================================================
# CLIENT PASSWORD CHANGE
# ============================================================

def client_password_change(request):

    # Client must be logged in
    if not request.user.is_authenticated:
        return redirect('account_login')

    # Staff/admin users should remain on admin side
    if request.user.is_staff:
        return redirect('admin_dashboard')

    return render(
        request,
        'client/password_change.html'
    )

# ==========================================================
# ADMIN ACCESS CONTROL
# ==========================================================

def is_admin(user):

    if not user.is_authenticated:
        return False

    if not user.is_staff:
        return False

    try:
        profile = user.profile
    except Profile.DoesNotExist:
        return False

    if profile.is_suspended:
        return False

    return profile.role in ['admin', 'staff']


def is_super_admin(user):

    if not user.is_authenticated:
        return False

    if not user.is_staff:
        return False

    try:
        profile = user.profile
    except Profile.DoesNotExist:
        return False

    if profile.is_suspended:
        return False

    return profile.role == 'admin'


# ==========================================================
# ADMIN LOGIN
# ==========================================================

def admin_login(request):

    if request.user.is_authenticated:

        if is_admin(request.user):
            return redirect('admin_dashboard')

        logout(request)

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        if not username or not password:

            messages.error(
                request,
                'Please enter your username and password.'
            )

            return render(
                request,
                'accounts/admin_login.html'
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:

            messages.error(
                request,
                'Invalid administrator credentials.'
            )

            return render(
                request,
                'accounts/admin_login.html'
            )

        if not user.is_staff:

            messages.error(
                request,
                'You do not have administrator access.'
            )

            return render(
                request,
                'accounts/admin_login.html'
            )

        try:

            profile = user.profile

        except Profile.DoesNotExist:

            messages.error(
                request,
                'Administrator profile not found.'
            )

            return render(
                request,
                'accounts/admin_login.html'
            )

        if profile.is_suspended:

            messages.error(
                request,
                'This administrator account has been suspended.'
            )

            return render(
                request,
                'accounts/admin_login.html'
            )

        if profile.role not in ['admin', 'staff']:

            messages.error(
                request,
                'You do not have administrator access.'
            )

            return render(
                request,
                'accounts/admin_login.html'
            )

        login(request, user)

        return redirect('admin_dashboard')

    return render(
        request,
        'accounts/admin_login.html'
    )


# ==========================================================
# LOGOUT
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def admin_logout(request):

    logout(request)

    return redirect('admin_login')


# ==========================================================
# USER LIST / READ
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def user_list(request):

    users = User.objects.select_related(
        'profile'
    ).all().order_by('-date_joined')

    # ------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------

    search = request.GET.get(
        'search',
        ''
    ).strip()

    if search:

        users = users.filter(

            Q(username__icontains=search)
            |
            Q(first_name__icontains=search)
            |
            Q(last_name__icontains=search)
            |
            Q(email__icontains=search)

        )

    # ------------------------------------------------------
    # ROLE FILTER
    # ------------------------------------------------------

    role = request.GET.get(
        'role',
        ''
    )

    if role:

        users = users.filter(
            profile__role=role
        )

    # ------------------------------------------------------
    # STATUS FILTER
    # ------------------------------------------------------

    status = request.GET.get(
        'status',
        ''
    )

    if status == 'active':

        users = users.filter(
            is_active=True,
            profile__is_suspended=False
        )

    elif status == 'suspended':

        users = users.filter(
            profile__is_suspended=True
        )

    elif status == 'inactive':

        users = users.filter(
            is_active=False
        )

    # ------------------------------------------------------
    # PAGINATION
    # ------------------------------------------------------

    paginator = Paginator(
        users,
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

        'selected_role': role,

        'selected_status': status,

        'total_users': User.objects.count(),

        'total_clients': Profile.objects.filter(
            role='client'
        ).count(),

        'total_owners': Profile.objects.filter(
            role='owner'
        ).count(),

        'total_staff': Profile.objects.filter(
            role='staff'
        ).count(),

        'total_admins': Profile.objects.filter(
            role='admin'
        ).count(),

        'total_suspended': Profile.objects.filter(
            is_suspended=True
        ).count(),

    }

    return render(
        request,
        'dashboard/users/user_list.html',
        context
    )


# ==========================================================
# CREATE USER
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def user_create(request):

    if request.method == 'POST':

        form = AdminUserCreateForm(
            request.POST
        )

        if form.is_valid():

            user = form.save()

            messages.success(
                request,
                f'User "{user.username}" was created successfully.'
            )

            return redirect(
                'user_detail',
                user_id=user.id
            )

    else:

        form = AdminUserCreateForm()

    return render(
        request,
        'dashboard/users/user_form.html',
        {
            'form': form,
            'page_title': 'Add User',
            'button_text': 'Create User',
        }
    )


# ==========================================================
# USER DETAILS
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def user_detail(request, user_id):

    user = get_object_or_404(
        User.objects.select_related(
            'profile'
        ),
        id=user_id
    )

    return render(
        request,
        'dashboard/users/user_detail.html',
        {
            'managed_user': user
        }
    )


# ==========================================================
# EDIT USER
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def user_edit(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id
    )

    if request.method == 'POST':

        form = AdminUserEditForm(
            request.POST,
            instance=user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                f'User "{user.username}" was updated successfully.'
            )

            return redirect(
                'user_detail',
                user_id=user.id
            )

    else:

        form = AdminUserEditForm(
            instance=user
        )

    return render(
        request,
        'dashboard/users/user_form.html',
        {
            'form': form,
            'page_title': f'Edit User: {user.username}',
            'button_text': 'Save Changes',
            'managed_user': user,
        }
    )


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def user_change_password(
    request,
    user_id
):

    user = get_object_or_404(
        User,
        id=user_id
    )

    if request.method == 'POST':

        form = AdminPasswordChangeForm(
            user,
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                f'Password for "{user.username}" was changed successfully.'
            )

            return redirect(
                'user_detail',
                user_id=user.id
            )

    else:

        form = AdminPasswordChangeForm(
            user
        )

    return render(
        request,
        'dashboard/users/password_form.html',
        {
            'form': form,
            'managed_user': user,
        }
    )


# ==========================================================
# SUSPEND USER
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def user_suspend(request, user_id):

    user = get_object_or_404(
        User.objects.select_related(
            'profile'
        ),
        id=user_id
    )

    if user == request.user:

        messages.error(
            request,
            'You cannot suspend your own account.'
        )

        return redirect(
            'user_detail',
            user_id=user.id
        )

    if request.method == 'POST':

        reason = request.POST.get(
            'reason',
            ''
        ).strip()

        profile = user.profile

        profile.is_suspended = True
        profile.suspension_reason = reason
        profile.save()

        user.is_active = False
        user.save(
            update_fields=['is_active']
        )

        messages.success(
            request,
            f'User "{user.username}" has been suspended.'
        )

        return redirect(
            'user_detail',
            user_id=user.id
        )

    return render(
        request,
        'dashboard/users/confirm_suspend.html',
        {
            'managed_user': user
        }
    )


# ==========================================================
# ACTIVATE USER
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def user_activate(request, user_id):

    user = get_object_or_404(
        User.objects.select_related(
            'profile'
        ),
        id=user_id
    )

    if request.method == 'POST':

        profile = user.profile

        profile.is_suspended = False
        profile.suspension_reason = ''

        profile.save()

        user.is_active = True

        user.save(
            update_fields=['is_active']
        )

        messages.success(
            request,
            f'User "{user.username}" has been activated.'
        )

    return redirect(
        'user_detail',
        user_id=user.id
    )


# ==========================================================
# DELETE USER
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def user_delete(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id
    )

    if user == request.user:

        messages.error(
            request,
            'You cannot delete your own administrator account.'
        )

        return redirect(
            'user_detail',
            user_id=user.id
        )

    if user.is_superuser:

        messages.error(
            request,
            'Super administrator accounts cannot be deleted from this dashboard.'
        )

        return redirect(
            'user_detail',
            user_id=user.id
        )

    if request.method == 'POST':

        username = user.username

        user.delete()

        messages.success(
            request,
            f'User "{username}" was deleted successfully.'
        )

        return redirect(
            'user_list'
        )

    return render(
        request,
        'dashboard/users/confirm_delete.html',
        {
            'managed_user': user
        }
    )