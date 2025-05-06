from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Country
from .serializers import CountrySerializer, CountryListSerializer, CountryCreateUpdateSerializer


class CountryViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Country.objects.all()
    # permission_classes = [IsAuthenticated]
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
        
        serializer = CountryListSerializer(same_region_countries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_language(self, request):
        language = request.query_params.get('language', None)
        if not language:
            return Response(
                {"error": "Language parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter countries with the specified language
        countries = []
        for country in Country.objects.all():
            if language.lower() in map(str.lower, country.languages.values()):
                countries.append(country)
        
        serializer = CountryListSerializer(countries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search for countries by name (partial match)"""
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Search query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        countries = Country.objects.filter(
            Q(name__icontains=query) | 
            Q(official_name__icontains=query)
        )
        
        serializer = CountryListSerializer(countries, many=True)
        return Response(serializer.data)


# API endpoint to return country list (using query parameters for search)
def country_list_view(request):
    search_query = request.GET.get('q', '')

    if search_query:
        countries = Country.objects.filter(
            Q(name__icontains=search_query) | 
            Q(official_name__icontains=search_query)
        )
    else:
        countries = Country.objects.all()

    countries_data = list(countries.values('id', 'name', 'official_name', 'region'))
    
    return JsonResponse({
        'search_query': search_query,
        'countries': countries_data
    })


# API endpoint to return country details with same region countries
def country_detail_view(request, country_id):
    country = get_object_or_404(Country, id=country_id)

    country_data = {
        'id': country.id,
        'name': country.name,
        'official_name': country.official_name,
        'region': country.region,
        'subregion': country.subregion,
        'population': country.population,
        'flag_url': country.flag,
        'languages': country.languages,
        'currencies': country.currencies,
        'borders': country.borders,
        'timezones': country.timezones
    }

    # Get countries in the same region, excluding the current country
    same_region_countries = list(
        Country.objects.filter(region=country.region)
        .exclude(id=country.id)
        .values('id', 'name', 'flag')
    )

    return JsonResponse({
        'country': country_data,
        'same_region_countries': same_region_countries
    })
