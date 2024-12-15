from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission

    REQUIRED_PERMISSIONS = [
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.FOREGROUND_SERVICE,
        Permission.POST_NOTIFICATIONS
    ]

    def check_and_request_permissions():
        """Request required Android permissions at runtime"""
        try:
            request_permissions(REQUIRED_PERMISSIONS)
        except Exception as e:
            print(f"Error requesting permissions: {e}")
            return False
        return True

else:
    def check_and_request_permissions():
        """Dummy function for non-Android platforms"""
        return True
