from django.db import models
from django.db.models import JSONField
from django.db.models import Q

class Country(models.Model):
    name = models.CharField(max_length=255)  # Common name
    official_name = models.CharField(max_length=255)
    cca2 = models.CharField(max_length=2, unique=True)
    cca3 = models.CharField(max_length=3, unique=True)
    flag = models.URLField(max_length=255)
    region = models.CharField(max_length=100)
    subregion = models.CharField(max_length=100, blank=True, null=True)
    population = models.BigIntegerField()
    
    # Store additional data as JSON
    languages = models.JSONField(default=dict, blank=True, null=True)
    timezones = models.JSONField(default=list, blank=True, null=True)
    capitals = models.JSONField(default=list, blank=True, null=True)
    currencies = models.JSONField(default=dict, blank=True, null=True)
    borders = models.JSONField(default=list, blank=True, null=True)
    
    # Store full JSON data for reference
    raw_data = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Countries'
        # Adding indexes to frequently filtered fields
        indexes = [
            models.Index(fields=['region']),
            models.Index(fields=['languages']),
            models.Index(fields=['borders']),
        ]
        
    def __str__(self):
        return self.name
    
    def get_capital(self):
        """Return the primary capital or first capital if many"""
        if self.capitals and len(self.capitals) > 0:
            return self.capitals[0]
        return "N/A"
    
    def get_primary_timezone(self):
        """Return the primary timezone or first timezone if many"""
        if self.timezones and len(self.timezones) > 0:
            return self.timezones[0]
        return "N/A"
    
    @classmethod
    def get_countries_by_language(cls, language):
        """Return countries that speak the given language"""
        return cls.objects.filter(languages__contains={language.lower(): True})
    
    @classmethod
    def get_countries_in_same_region(cls, region):
        """Return countries in the same region"""
        return cls.objects.filter(region=region)
    
    @classmethod
    def search_countries(cls, query):
        """Search for countries by name (partial match)"""
        return cls.objects.filter(
            Q(name__icontains=query) | Q(official_name__icontains=query)
        )
    
    @classmethod
    def get_countries_with_borders(cls, borders):
        """Return countries that share borders with the given list of countries"""
        return cls.objects.filter(borders__overlap=borders)
