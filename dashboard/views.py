from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from accounts.views import is_admin


@user_passes_test(
    is_admin,
    login_url='/admin-login/'
)
def admin_dashboard(request):

    context = {

        'total_users': User.objects.count(),

        'total_clients': 0,

        'total_owners': 0,

        'total_properties': 0,

        'total_bookings': 0,

        'total_revenue': 0,

    }

    return render(
        request,
        'dashboard/dashboard.html',
        context
    )