from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'countries', views.CountryViewSet)


urlpatterns = [
    # API endpoints using the router
    path('api/', include(router.urls)),
    
    # Web interface URLs
    path('countries/', views.country_list_view, name='country_list'),
    path('countries/<int:country_id>/', views.country_detail_view, name='country_detail'),
]