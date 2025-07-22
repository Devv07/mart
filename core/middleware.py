from django.shortcuts import redirect
from django.urls import reverse

class RoleBasedRedirectMiddleware:
    @staticmethod
    def redirect_based_on_role(user):
        if user.role == 'vendor':
            return redirect('vendor:dashboard')
        elif user.role == 'user':
            return redirect('user:dashboard')
        else:
            return redirect('home')