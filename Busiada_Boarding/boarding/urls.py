from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('admissions/', views.admissions, name='admissions'),
    path('academics/', views.academics, name='academics'),
    path('academics/8-4-4/', views.academics_844, name='academics_844'),
    path('academics/2-6-3-3-3/', views.academics_26333, name='academics_26333'),
    path('boarding/', views.boarding_page, name='boarding'),
    path('page/<slug:slug>/', views.site_page, name='site_page'),
    path('inquiry/', views.submit_inquiry, name='submit_inquiry'),
    # AI endpoints removed — no external AI integration in production
    path('announcements/', views.announcements, name='announcements'),
]