from django.urls import path
from . import views
from . import views_ai

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('admissions/', views.admissions, name='admissions'),
    path('history/', views.school_history, name='school_history'),
    path('school-anthem/', views.school_anthem, name='school_anthem'),
    path('school-leadership/', views.school_leadership, name='school_leadership'),
    path('school-chaplaincy/', views.school_chaplaincy, name='school_chaplaincy'),
    path('strategic-plan/', views.strategic_plan, name='strategic_plan'),
    path('service-charter/', views.service_charter, name='service_charter'),
    path('contact/', views.contact_page, name='contact_page'),
    path('fees/', views.fee_payment, name='fee_payment'),
    path('academics/', views.academics, name='academics'),
    path('academics/8-4-4/', views.academics_844, name='academics_844'),
    path('academics/2-6-3-3-3/', views.academics_26333, name='academics_26333'),
    path('boarding/', views.boarding_page, name='boarding'),
    path('page/<slug:slug>/', views.site_page, name='site_page'),
    path('inquiry/', views.submit_inquiry, name='submit_inquiry'),
    # AI endpoints
    path('ai/admin/suggest/', views_ai.admin_suggest, name='ai_admin_suggest'),
    path('ai/chat/', views_ai.user_chat, name='ai_user_chat'),
    path('announcements/', views.announcements, name='announcements'),
]