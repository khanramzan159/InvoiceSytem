from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.home),
    path('login', views.login),
    path('signup', views.signup),
    path('logout', views.logout),
    path('changepass', views.changep),
    path('change_pass', views.changepassword),
    path('admin/', views.admin),
    path('admin/view', views.view),
    path('admin/save', views.save),
    path('admin/delete', views.delete),
    path('admin/block', views.block),
    path('admin/logout', views.adminlogout),
    path('admin/search', views.search),
    path('admin/create', views.create),
    path('admin/admin_invoices', views.admin_invoices),
    path('admin/admin_create_invoice', views.admin_create_invoice),
    path('admin_update_invoice/<int:invoice_id>/', views.admin_update_invoice, name='admin_update_invoice'),
    path('admin_delete_invoice/<int:invoice_id>/', views.admin_delete_invoice, name='admin_delete_invoice'),

    path('create_invoice', views.create_invoice),
    path('update_invoice/<int:invoice_id>/', views.update_invoice, name='update_invoice'),
    path('delete_invoice/<int:invoice_id>/', views.delete_invoice, name='delete_invoice'),
]