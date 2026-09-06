from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import Review
from .forms import ReviewForm


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
def review_dashboard(request):

    reviews = Review.objects.all()

    approved = reviews.filter(status='approved')
    pending = reviews.filter(status='pending')
    rejected = reviews.filter(status='rejected')
    flagged = reviews.filter(is_flagged=True)

    average_rating = reviews.aggregate(
        average=Avg('rating')
    )['average'] or 0

    rating_distribution = {
        5: reviews.filter(rating=5).count(),
        4: reviews.filter(rating=4).count(),
        3: reviews.filter(rating=3).count(),
        2: reviews.filter(rating=2).count(),
        1: reviews.filter(rating=1).count(),
    }

    context = {
        'total_reviews': reviews.count(),
        'approved_reviews': approved.count(),
        'pending_reviews': pending.count(),
        'rejected_reviews': rejected.count(),
        'flagged_reviews': flagged.count(),
        'average_rating': round(average_rating, 1),
        'rating_distribution': rating_distribution,
        'recent_reviews': reviews.select_related(
            'client',
            'property',
            'booking'
        )[:10],
    }

    return render(
        request,
        'dashboard/reviews/dashboard.html',
        context
    )


@admin_required
def review_list(request):

    reviews = Review.objects.select_related(
        'client',
        'property',
        'booking'
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    rating = request.GET.get('rating', '').strip()
    flagged = request.GET.get('flagged', '').strip()

    if search:
        reviews = reviews.filter(
            Q(title__icontains=search) |
            Q(comment__icontains=search) |
            Q(client__username__icontains=search) |
            Q(client__first_name__icontains=search) |
            Q(client__last_name__icontains=search) |
            Q(property__name__icontains=search)
        )

    if status:
        reviews = reviews.filter(status=status)

    if rating:
        reviews = reviews.filter(rating=rating)

    if flagged == 'yes':
        reviews = reviews.filter(is_flagged=True)

    context = {
        'reviews': reviews,
        'search': search,
        'selected_status': status,
        'selected_rating': rating,
        'selected_flagged': flagged,
        'status_choices': Review.MODERATION_STATUS,
        'rating_choices': Review.RATING_CHOICES,
    }

    return render(
        request,
        'dashboard/reviews/review_list.html',
        context
    )


@admin_required
def review_detail(request, pk):

    review = get_object_or_404(
        Review.objects.select_related(
            'client',
            'property',
            'booking'
        ),
        pk=pk
    )

    return render(
        request,
        'dashboard/reviews/review_detail.html',
        {'review': review}
    )


@admin_required
def review_create(request):

    if request.method == 'POST':

        form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save()

            messages.success(
                request,
                f'Review #{review.pk} created successfully.'
            )

            return redirect(
                'review_detail',
                pk=review.pk
            )

    else:
        form = ReviewForm()

    return render(
        request,
        'dashboard/reviews/review_form.html',
        {
            'form': form,
            'title': 'Add Review'
        }
    )


@admin_required
def review_edit(request, pk):

    review = get_object_or_404(
        Review,
        pk=pk
    )

    if request.method == 'POST':

        form = ReviewForm(
            request.POST,
            instance=review
        )

        if form.is_valid():

            review = form.save()

            messages.success(
                request,
                'Review updated successfully.'
            )

            return redirect(
                'review_detail',
                pk=review.pk
            )

    else:
        form = ReviewForm(
            instance=review
        )

    return render(
        request,
        'dashboard/reviews/review_form.html',
        {
            'form': form,
            'review': review,
            'title': 'Edit Review'
        }
    )


@admin_required
def review_delete(request, pk):

    review = get_object_or_404(
        Review,
        pk=pk
    )

    if request.method == 'POST':

        review_id = review.pk

        review.delete()

        messages.success(
            request,
            f'Review #{review_id} deleted successfully.'
        )

        return redirect('review_list')

    return render(
        request,
        'dashboard/reviews/review_delete.html',
        {'review': review}
    )


@admin_required
def approve_review(request, pk):

    review = get_object_or_404(
        Review,
        pk=pk
    )

    if request.method == 'POST':

        review.status = 'approved'
        review.moderated_at = timezone.now()
        review.save(
            update_fields=[
                'status',
                'moderated_at',
                'updated_at'
            ]
        )

        messages.success(
            request,
            'Review approved successfully.'
        )

    return redirect(
        'review_detail',
        pk=review.pk
    )


@admin_required
def reject_review(request, pk):

    review = get_object_or_404(
        Review,
        pk=pk
    )

    if request.method == 'POST':

        review.status = 'rejected'
        review.moderated_at = timezone.now()
        review.save(
            update_fields=[
                'status',
                'moderated_at',
                'updated_at'
            ]
        )

        messages.warning(
            request,
            'Review rejected.'
        )

    return redirect(
        'review_detail',
        pk=review.pk
    )


@admin_required
def toggle_flag_review(request, pk):

    review = get_object_or_404(
        Review,
        pk=pk
    )

    if request.method == 'POST':

        review.is_flagged = not review.is_flagged
        review.save(
            update_fields=[
                'is_flagged',
                'updated_at'
            ]
        )

        if review.is_flagged:
            messages.warning(
                request,
                'Review has been flagged.'
            )
        else:
            messages.success(
                request,
                'Review flag removed.'
            )

    return redirect(
        'review_detail',
        pk=review.pk
    )