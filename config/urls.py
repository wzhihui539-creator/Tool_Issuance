from django.contrib import admin
from django.urls import path, include
from accounts import views as acc_views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", acc_views.home, name="home"),
    path("login/", acc_views.login_view, name="login"),
    path("logout/", acc_views.logout_view, name="logout"),

    path("worker/", acc_views.worker_page),
    path("keeper/", acc_views.keeper_page),
    path("supervisor/", acc_views.supervisor_page),

    path("inventory/", include("inventory.urls")),
    path("requisitions/", include("requisition.urls")),

]
