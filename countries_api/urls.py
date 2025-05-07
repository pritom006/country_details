from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CustomLogoutView

router = DefaultRouter()
router.register(r'countries', views.CountryViewSet)


urlpatterns = [
    # API endpoints using the router
    path('api/', include(router.urls)),
    
    # Authentication URLs
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/register/', views.register_view, name='register'),

    # Web interface URLs
    path('countries/', views.country_list_view, name='country_list'),
    path('countries/<int:country_id>/', views.country_detail_view, name='country_detail'),
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),
]