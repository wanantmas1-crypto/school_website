from django.urls import path
from . import views
from . import views_ai

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('admissions/', views.admissions, name='admissions'),
    path('academics/', views.academics, name='academics'),
    path('boarding/', views.boarding_page, name='boarding'),
    path('page/<slug:slug>/', views.site_page, name='site_page'),
    path('inquiry/', views.submit_inquiry, name='submit_inquiry'),
    # AI endpoints
    path('ai/admin/suggest/', views_ai.admin_suggest, name='ai_admin_suggest'),
    path('ai/chat/', views_ai.user_chat, name='ai_user_chat'),
    path('announcements/', views.announcements, name='announcements'),
]