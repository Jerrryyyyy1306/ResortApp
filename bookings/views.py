from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q, Sum
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.utils import timezone

from .models import Booking
from .forms import BookingAdminForm


def is_admin(user):

    return (
        user.is_authenticated
        and user.is_staff
    )


def is_super_admin(user):

    return (
        user.is_authenticated
        and user.is_staff
        and getattr(
            getattr(user, 'profile', None),
            'role',
            None
        ) == 'admin'
    )


# ==========================================================
# BOOKING DASHBOARD
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def booking_dashboard(request):

    bookings = Booking.objects.all()

    total_bookings = bookings.count()

    pending_bookings = bookings.filter(
        status='pending'
    ).count()

    confirmed_bookings = bookings.filter(
        status='confirmed'
    ).count()

    checked_in_bookings = bookings.filter(
        status='checked_in'
    ).count()

    completed_bookings = bookings.filter(
        status='completed'
    ).count()

    cancelled_bookings = bookings.filter(
        status='cancelled'
    ).count()

    rejected_bookings = bookings.filter(
        status='rejected'
    ).count()

    total_revenue = bookings.filter(
        status__in=[
            'confirmed',
            'checked_in',
            'completed'
        ]
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    total_paid = bookings.aggregate(
        total=Sum('amount_paid')
    )['total'] or 0

    outstanding = (
        total_revenue - total_paid
    )

    recent_bookings = bookings.select_related(
        'client',
        'property',
        'room'
    ).order_by(
        '-created_at'
    )[:10]

    context = {

        'total_bookings':
            total_bookings,

        'pending_bookings':
            pending_bookings,

        'confirmed_bookings':
            confirmed_bookings,

        'checked_in_bookings':
            checked_in_bookings,

        'completed_bookings':
            completed_bookings,

        'cancelled_bookings':
            cancelled_bookings,

        'rejected_bookings':
            rejected_bookings,

        'total_revenue':
            total_revenue,

        'total_paid':
            total_paid,

        'outstanding':
            outstanding,

        'recent_bookings':
            recent_bookings,
    }

    return render(
        request,
        'dashboard/bookings/booking_dashboard.html',
        context
    )


# ==========================================================
# ALL BOOKINGS
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def booking_list(request):

    bookings = Booking.objects.select_related(
        'client',
        'property',
        'room'
    ).all()

    search = request.GET.get(
        'search',
        ''
    ).strip()

    status = request.GET.get(
        'status',
        ''
    )

    payment_status = request.GET.get(
        'payment_status',
        ''
    )

    date = request.GET.get(
        'date',
        ''
    )

    if search:

        bookings = bookings.filter(

            Q(booking_reference__icontains=search)
            |
            Q(client__username__icontains=search)
            |
            Q(client__first_name__icontains=search)
            |
            Q(client__last_name__icontains=search)
            |
            Q(property__name__icontains=search)

        )

    if status:

        bookings = bookings.filter(
            status=status
        )

    if payment_status:

        bookings = bookings.filter(
            payment_status=payment_status
        )

    if date:

        bookings = bookings.filter(
            check_in=date
        )

    bookings = bookings.order_by(
        '-created_at'
    )

    context = {

        'bookings': bookings,

        'search': search,

        'selected_status': status,

        'selected_payment_status':
            payment_status,

        'selected_date': date,

    }

    return render(
        request,
        'dashboard/bookings/booking_list.html',
        context
    )


# ==========================================================
# BOOKING DETAILS
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def booking_detail(
    request,
    booking_id
):

    booking = get_object_or_404(
        Booking.objects.select_related(
            'client',
            'property',
            'room'
        ),
        id=booking_id
    )

    return render(
        request,
        'dashboard/bookings/booking_detail.html',
        {
            'booking': booking
        }
    )


# ==========================================================
# CREATE BOOKING
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def booking_create(request):

    if request.method == 'POST':

        form = BookingAdminForm(
            request.POST
        )

        if form.is_valid():

            booking = form.save()

            messages.success(
                request,
                f'Booking {booking.booking_reference} '
                f'was created successfully.'
            )

            return redirect(
                'booking_detail',
                booking_id=booking.id
            )

    else:

        form = BookingAdminForm()

    return render(
        request,
        'dashboard/bookings/booking_form.html',
        {
            'form': form,
            'page_title': 'Create Booking',
            'button_text': 'Create Booking',
        }
    )


# ==========================================================
# EDIT BOOKING
# ==========================================================

@user_passes_test(
    is_super_admin,
    login_url='/admin-login/'
)
def booking_edit(
    request,
    booking_id
):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    if request.method == 'POST':

        form = BookingAdminForm(
            request.POST,
            instance=booking
        )

        if form.is_valid():

            booking = form.save()

            messages.success(
                request,
                f'Booking {booking.booking_reference} '
                f'was updated successfully.'
            )

            return redirect(
                'booking_detail',
                booking_id=booking.id
            )

    else:

        form = BookingAdminForm(
            instance=booking
        )

    return render(
        request,
        'dashboard/bookings/booking_form.html',
        {
            'form': form,
            'page_title':
                f'Edit {booking.booking_reference}',
            'button_text':
                'Save Changes',
            'booking': booking,
        }
    )


# ==========================================================
# CONFIRM BOOKING
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def booking_confirm(
    request,
    booking_id
):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    if request.method == 'POST':

        if booking.status != 'pending':

            messages.error(
                request,
                'Only pending bookings can be confirmed.'
            )

            return redirect(
                'booking_detail',
                booking_id=booking.id
            )

        booking.status = 'confirmed'

        booking.confirmed_at = timezone.now()

        booking.save(
            update_fields=[
                'status',
                'confirmed_at',
                'updated_at'
            ]
        )

        messages.success(
            request,
            f'Booking {booking.booking_reference} '
            f'has been confirmed.'
        )

    return redirect(
        'booking_detail',
        booking_id=booking.id
    )


# ==========================================================
# CHECK IN
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def booking_check_in(
    request,
    booking_id
):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    if request.method == 'POST':

        if booking.status != 'confirmed':

            messages.error(
                request,
                'Only confirmed bookings can be checked in.'
            )

            return redirect(
                'booking_detail',
                booking_id=booking.id
            )

        booking.status = 'checked_in'

        booking.checked_in_at = timezone.now()

        booking.save(
            update_fields=[
                'status',
                'checked_in_at',
                'updated_at'
            ]
        )

        messages.success(
            request,
            f'{booking.booking_reference} '
            f'has been checked in.'
        )

    return redirect(
        'booking_detail',
        booking_id=booking.id
    )


# ==========================================================
# COMPLETE BOOKING
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def booking_complete(
    request,
    booking_id
):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    if request.method == 'POST':

        if booking.status != 'checked_in':

            messages.error(
                request,
                'Only checked-in bookings can be completed.'
            )

            return redirect(
                'booking_detail',
                booking_id=booking.id
            )

        booking.status = 'completed'

        booking.completed_at = timezone.now()

        booking.save(
            update_fields=[
                'status',
                'completed_at',
                'updated_at'
            ]
        )

        messages.success(
            request,
            f'{booking.booking_reference} '
            f'has been completed.'
        )

    return redirect(
        'booking_detail',
        booking_id=booking.id
    )


# ==========================================================
# CANCEL BOOKING
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def booking_cancel(
    request,
    booking_id
):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    if request.method == 'POST':

        reason = request.POST.get(
            'reason',
            ''
        ).strip()

        if booking.status in [
            'completed',
            'cancelled',
            'rejected'
        ]:

            messages.error(
                request,
                'This booking cannot be cancelled.'
            )

            return redirect(
                'booking_detail',
                booking_id=booking.id
            )

        booking.status = 'cancelled'

        booking.cancellation_reason = reason

        booking.cancelled_at = timezone.now()

        booking.save(
            update_fields=[
                'status',
                'cancellation_reason',
                'cancelled_at',
                'updated_at'
            ]
        )

        messages.success(
            request,
            f'Booking {booking.booking_reference} '
            f'has been cancelled.'
        )

    return redirect(
        'booking_detail',
        booking_id=booking.id
    )


# ==========================================================
# REJECT BOOKING
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def booking_reject(
    request,
    booking_id
):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    if request.method == 'POST':

        if booking.status != 'pending':

            messages.error(
                request,
                'Only pending bookings can be rejected.'
            )

            return redirect(
                'booking_detail',
                booking_id=booking.id
            )

        reason = request.POST.get(
            'reason',
            ''
        ).strip()

        booking.status = 'rejected'

        booking.rejection_reason = reason

        booking.save(
            update_fields=[
                'status',
                'rejection_reason',
                'updated_at'
            ]
        )

        messages.success(
            request,
            f'Booking {booking.booking_reference} '
            f'has been rejected.'
        )

    return redirect(
        'booking_detail',
        booking_id=booking.id
    )


# ==========================================================
# RECORD PAYMENT
# ==========================================================

@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def booking_payment(
    request,
    booking_id
):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    if request.method == 'POST':

        try:

            amount = float(
                request.POST.get(
                    'amount',
                    0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            amount = 0

        if amount <= 0:

            messages.error(
                request,
                'Enter a valid payment amount.'
            )

            return redirect(
                'booking_detail',
                booking_id=booking.id
            )

        new_amount = (
            booking.amount_paid + amount
        )

        if new_amount > booking.total_amount:

            messages.error(
                request,
                'Payment cannot exceed the booking balance.'
            )

            return redirect(
                'booking_detail',
                booking_id=booking.id
            )

        booking.amount_paid = new_amount

        if (
            booking.amount_paid
            >= booking.total_amount
        ):

            booking.payment_status = 'paid'

        elif booking.amount_paid > 0:

            booking.payment_status = 'partial'

        else:

            booking.payment_status = 'unpaid'

        booking.save(
            update_fields=[
                'amount_paid',
                'payment_status',
                'updated_at'
            ]
        )

        messages.success(
            request,
            'Payment recorded successfully.'
        )

    return redirect(
        'booking_detail',
        booking_id=booking.id
    )