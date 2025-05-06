from rest_framework import serializers
from .models import Country

class CountrySerializer(serializers.ModelSerializer):
    capital = serializers.SerializerMethodField()
    primary_timezone = serializers.SerializerMethodField()
    
    class Meta:
        model = Country
        fields = [
            'id', 'name', 'official_name', 'cca2', 'cca3', 'flag',
            'region', 'subregion', 'population', 'capital', 'primary_timezone',
            'languages', 'currencies', 'borders', 'timezones', 'capitals',
            'created_at', 'updated_at'
        ]
    
    def get_capital(self, obj):
        return obj.get_capital()
    
    def get_primary_timezone(self, obj):
        return obj.get_primary_timezone()

class CountryListSerializer(serializers.ModelSerializer):
    capital = serializers.SerializerMethodField()
    
    class Meta:
        model = Country
        fields = ['id', 'name', 'cca2', 'flag', 'region', 'population', 'capital']
    
    def get_capital(self, obj):
        return obj.get_capital()

class CountryCreateUpdateSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Country
        fields = [
            'name', 'official_name', 'cca2', 'cca3', 'flag',
            'region', 'subregion', 'population', 'languages',
            'timezones', 'capitals', 'currencies', 'borders'
        ]
    
    def create(self, validated_data):
        return Country.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class CountryPaginationSerializer(serializers.ModelSerializer):
    """Serializer for paginated country lists"""
    capital = serializers.SerializerMethodField()
    
    class Meta:
        model = Country
        fields = ['id', 'name', 'cca2', 'flag', 'region', 'population', 'capital']
    
    def get_capital(self, obj):
        return obj.get_capital()
