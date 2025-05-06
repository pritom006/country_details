from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include the countries_api URLs
    path('', include('countries_api.urls')),
    
    # Root URL redirects to countries list
    path('', RedirectView.as_view(pattern_name='country_list', permanent=False)),
]