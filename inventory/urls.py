from django.urls import path
from . import views

urlpatterns = [
    path("items/", views.ItemListView.as_view(), name="item_list"),
    path("items/new/", views.ItemCreateView.as_view(), name="item_create"),
    path("items/<int:pk>/", views.ItemDetailView.as_view(), name="item_detail"),
    path("items/<int:pk>/edit/", views.ItemUpdateView.as_view(), name="item_update"),
    path("items/<int:pk>/delete/", views.ItemDeleteView.as_view(), name="item_delete"),
    path("stock/", views.stock_list, name="stock_list"),
    path("txns/", views.txn_list, name="txn_list"),
    path("stock/in/", views.stock_in, name="stock_in"),
    path("stock/out/", views.stock_out, name="stock_out"),
    path("stock/low/", views.low_stock_list, name="low_stock_list"),

]
