from django.urls import path
from . import views

urlpatterns = [
    path("", views.requisition_list, name="req_list"),
    path("new/", views.requisition_create, name="req_create"),
    path("<int:pk>/", views.requisition_detail, name="req_detail"),
    path("<int:pk>/issue/", views.requisition_issue, name="req_issue"),
]