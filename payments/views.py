from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import Payment
from .forms import PaymentForm


def admin_required(view_func):

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:

            return redirect('account_login')

        if not request.user.is_staff:

            messages.error(
                request,
                'You do not have permission to access this page.'
            )

            return redirect('admin_dashboard')

        return view_func(request, *args, **kwargs)

    return wrapper


@admin_required
def payment_dashboard(request):

    payments = Payment.objects.all()

    successful = payments.filter(
        status='successful'
    )

    pending = payments.filter(
        status='pending'
    )

    refunded = payments.filter(
        status='refunded'
    )

    failed = payments.filter(
        status='failed'
    )

    total_revenue = (
        successful.aggregate(
            total=Sum('amount')
        )['total']
        or 0
    )

    total_pending = (
        pending.aggregate(
            total=Sum('amount')
        )['total']
        or 0
    )

    total_refunded = (
        refunded.aggregate(
            total=Sum('amount')
        )['total']
        or 0
    )

    context = {

        'total_payments': payments.count(),

        'successful_payments': successful.count(),

        'pending_payments': pending.count(),

        'failed_payments': failed.count(),

        'refunded_payments': refunded.count(),

        'total_revenue': total_revenue,

        'total_pending': total_pending,

        'total_refunded': total_refunded,

        'recent_payments': payments.order_by(
            '-created_at'
        )[:10],
    }

    return render(
        request,
        'dashboard/payments/dashboard.html',
        context
    )


@admin_required
def payment_list(request):

    payments = Payment.objects.select_related(
        'booking',
        'client'
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()

    status = request.GET.get('status', '').strip()

    method = request.GET.get('method', '').strip()

    if search:

        payments = payments.filter(
            Q(payment_reference__icontains=search)
            |
            Q(transaction_id__icontains=search)
            |
            Q(client__username__icontains=search)
            |
            Q(client__first_name__icontains=search)
            |
            Q(client__last_name__icontains=search)
            |
            Q(booking__booking_reference__icontains=search)
        )

    if status:

        payments = payments.filter(
            status=status
        )

    if method:

        payments = payments.filter(
            payment_method=method
        )

    context = {
        'payments': payments,
        'search': search,
        'selected_status': status,
        'selected_method': method,
        'status_choices': Payment.PAYMENT_STATUS,
        'method_choices': Payment.PAYMENT_METHODS,
    }

    return render(
        request,
        'dashboard/payments/payment_list.html',
        context
    )


@admin_required
def payment_detail(request, pk):

    payment = get_object_or_404(
        Payment,
        pk=pk
    )

    return render(
        request,
        'dashboard/payments/payment_detail.html',
        {
            'payment': payment
        }
    )


@admin_required
def payment_create(request):

    if request.method == 'POST':

        form = PaymentForm(
            request.POST
        )

        if form.is_valid():

            payment = form.save()

            messages.success(
                request,
                f'Payment {payment.payment_reference} created successfully.'
            )

            return redirect(
                'payment_detail',
                pk=payment.pk
            )

    else:

        form = PaymentForm()

    return render(
        request,
        'dashboard/payments/payment_form.html',
        {
            'form': form,
            'title': 'Record Payment'
        }
    )


@admin_required
def payment_edit(request, pk):

    payment = get_object_or_404(
        Payment,
        pk=pk
    )

    if request.method == 'POST':

        form = PaymentForm(
            request.POST,
            instance=payment
        )

        if form.is_valid():

            payment = form.save()

            messages.success(
                request,
                'Payment updated successfully.'
            )

            return redirect(
                'payment_detail',
                pk=payment.pk
            )

    else:

        form = PaymentForm(
            instance=payment
        )

    return render(
        request,
        'dashboard/payments/payment_form.html',
        {
            'form': form,
            'payment': payment,
            'title': 'Edit Payment'
        }
    )


@admin_required
def payment_delete(request, pk):

    payment = get_object_or_404(
        Payment,
        pk=pk
    )

    if request.method == 'POST':

        reference = payment.payment_reference

        payment.delete()

        messages.success(
            request,
            f'Payment {reference} deleted successfully.'
        )

        return redirect(
            'payment_list'
        )

    return render(
        request,
        'dashboard/payments/payment_delete.html',
        {
            'payment': payment
        }
    )


@admin_required
def mark_payment_successful(request, pk):

    payment = get_object_or_404(
        Payment,
        pk=pk
    )

    if request.method == 'POST':

        payment.status = 'successful'

        if not payment.paid_at:

            payment.paid_at = timezone.now()

        payment.save()

        messages.success(
            request,
            f'Payment {payment.payment_reference} marked as successful.'
        )

    return redirect(
        'payment_detail',
        pk=payment.pk
    )


@admin_required
def mark_payment_failed(request, pk):

    payment = get_object_or_404(
        Payment,
        pk=pk
    )

    if request.method == 'POST':

        payment.status = 'failed'

        payment.save()

        messages.warning(
            request,
            f'Payment {payment.payment_reference} marked as failed.'
        )

    return redirect(
        'payment_detail',
        pk=payment.pk
    )