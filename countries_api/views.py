from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Country
from .serializers import (
    CountryCreateUpdateSerializer,
    CountryListSerializer,
    CountrySerializer,
)


class CountryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Country.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'official_name', 'cca2', 'cca3', 'region', 'subregion']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CountryListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CountryCreateUpdateSerializer
        return CountrySerializer
    
    @action(detail=True, methods=['get'])
    def same_region(self, request, pk=None):
        country = self.get_object()
        same_region_countries = Country.objects.filter(
            region=country.region
        ).exclude(id=country.id)
        
        # Pass data to template
        return render(request, 'countries/same_region.html', {
            'country': country,
            'same_region_countries': same_region_countries
        })
    
    @action(detail=False, methods=['get'])
    def by_language(self, request):
        language = request.query_params.get('language', None)
        error = None
        countries = []
        
        if not language:
            error = "Language parameter is required"
        else:
            for country in Country.objects.all():
                if language.lower() in map(str.lower, country.languages.values()):
                    countries.append(country)
        
        return render(request, 'countries/by_language.html', {
            'language': language,
            'countries': countries,
            'error': error
        })
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        error = None
        countries = []
        
        if not query:
            error = "Search query parameter 'q' is required"
        else:
            countries = Country.objects.filter(
                Q(name__icontains=query) | 
                Q(official_name__icontains=query)
            )
        
        return render(request, 'countries/search_results.html', {
            'query': query,
            'countries': countries,
            'error': error
        })


@login_required
def country_list_view(request):
    search_query = request.GET.get('q', '')

    if search_query:
        countries = Country.objects.filter(
            Q(name__icontains=search_query) | 
            Q(official_name__icontains=search_query)
        )
    else:
        countries = Country.objects.all()

    # Add pagination with 10 objects per page
    paginator = Paginator(countries, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'countries/country_list.html', {
        'search_query': search_query,
        'countries': page_obj  
    })


@login_required
def country_detail_view(request, country_id):
    country = get_object_or_404(Country, id=country_id)

    same_region_countries = Country.objects.filter(region=country.region).exclude(id=country.id)

    return render(request, 'countries/country_detail.html', {
        'country': country,
        'same_region_countries': same_region_countries
    })


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f"Account created for {username}! You are now logged in.")
            return redirect('country_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            # Redirect to a success page
            next_url = request.GET.get('next', 'country_list')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'registration/login.html')


class CustomLogoutView(SuccessMessageMixin, LogoutView):
    next_page = 'login'
    success_message = "You have successfully logged out."