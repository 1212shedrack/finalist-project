from django.urls import path
from accounts.views import auth_views, farmer_views, admin_views

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('register/', auth_views.register, name='register'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('password-reset/', auth_views.password_reset_request, name='password_reset'),
    path('password-reset/done/', auth_views.password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.password_reset_complete, name='password_reset_complete'),

    # Farmer Dashboard
    path('dashboard/', farmer_views.dashboard_redirect, name='dashboard'),
    path('dashboard/farmer/', farmer_views.farmer_dashboard, name='farmer_dashboard'),
    path('dashboard/farmer/profile/', farmer_views.farmer_profile, name='farmer_profile'),
    path('dashboard/farmer/avatar/', farmer_views.farmer_avatar_update, name='farmer_avatar'),
    path('dashboard/farmer/password/', farmer_views.farmer_change_password, name='farmer_password'),
    path('dashboard/farmer/history/', farmer_views.farmer_scan_history, name='farmer_history'),
    path('dashboard/farmer/favorites/', farmer_views.farmer_favorites, name='farmer_favorites'),
    path('dashboard/farmer/favorites/add/<int:pk>/', farmer_views.favorite_add, name='favorite_add'),
    path('dashboard/farmer/favorites/remove/<int:pk>/', farmer_views.favorite_remove, name='favorite_remove'),
    path('dashboard/farmer/notifications/', farmer_views.farmer_notifications, name='farmer_notifications'),
    path('dashboard/farmer/notifications/read/<int:pk>/', farmer_views.notification_mark_read, name='notification_read'),
    path('dashboard/farmer/feedback/', farmer_views.farmer_feedback, name='farmer_feedback'),
    path('dashboard/farmer/delete-account/', farmer_views.farmer_delete_account, name='farmer_delete_account'),

    # Admin Dashboard
    path('dashboard/admin/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/farmers/', admin_views.admin_farmers, name='admin_farmers'),
    path('dashboard/admin/farmers/<int:user_id>/', admin_views.admin_farmer_detail, name='admin_farmer_detail'),
    path('dashboard/admin/farmers/<int:user_id>/toggle/', admin_views.admin_toggle_active, name='admin_toggle_active'),
    path('dashboard/admin/farmers/<int:user_id>/delete/', admin_views.admin_delete_farmer, name='admin_delete_farmer'),
    path('dashboard/admin/farmers/<int:user_id>/reset-password/', admin_views.admin_reset_password, name='admin_reset_password'),
    path('dashboard/admin/scans/', admin_views.admin_all_scans, name='admin_scans'),
    path('dashboard/admin/reports/', admin_views.admin_reports, name='admin_reports'),
    path('dashboard/admin/feedback/', admin_views.admin_feedback, name='admin_feedback'),
    path('dashboard/admin/feedback/<int:pk>/resolve/', admin_views.admin_resolve_feedback, name='admin_resolve_feedback'),
    path('dashboard/admin/logs/', admin_views.admin_logs, name='admin_logs'),
    path('dashboard/admin/notify/', admin_views.admin_send_notification, name='admin_notify'),
    path('dashboard/admin/notify/<int:user_id>/', admin_views.admin_send_notification, name='admin_notify_user'),
    path('dashboard/admin/api/chart-data/', admin_views.admin_chart_data, name='admin_chart_data'),
]
