from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def moderator_required(view_func):
    def check_moderator(user):
        return user.is_authenticated and (user.is_staff or user.has_perm('media_archive.can_moderate'))
    return user_passes_test(check_moderator)(view_func)

def admin_required(view_func):
    def check_admin(user):
        return user.is_authenticated and user.is_staff
    return user_passes_test(check_admin)(view_func)