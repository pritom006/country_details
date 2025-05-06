import requests
from .models import Country
import logging

logger = logging.getLogger(__name__)

API_URL = "https://restcountries.com/v3.1/all"

def fetch_and_store_countries():
    """
    Fetch country data from the REST Countries API and store it in the database.
    """
    try:
        logger.info("Fetching countries data from API...")
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        countries_data = response.json()
        
        count_created = 0
        count_updated = 0
        
        for country_data in countries_data:
            # Extract required data
            name = country_data.get('name', {}).get('common', '')
            official_name = country_data.get('name', {}).get('official', '')
            cca2 = country_data.get('cca2', '')
            cca3 = country_data.get('cca3', '')
            flag = country_data.get('flags', {}).get('png', '')
            region = country_data.get('region', '')
            subregion = country_data.get('subregion', '')
            population = country_data.get('population', 0)
            
            # Extract additional data
            languages = country_data.get('languages', {})
            timezones = country_data.get('timezones', [])
            capitals = country_data.get('capital', [])
            currencies = country_data.get('currencies', {})
            borders = country_data.get('borders', [])
            
            # Update or create the country
            country, created = Country.objects.update_or_create(
                cca3=cca3,
                defaults={
                    'name': name,
                    'official_name': official_name,
                    'cca2': cca2,
                    'flag': flag,
                    'region': region,
                    'subregion': subregion,
                    'population': population,
                    'languages': languages,
                    'timezones': timezones,
                    'capitals': capitals,
                    'currencies': currencies,
                    'borders': borders,
                    'raw_data': country_data,
                }
            )
            
            if created:
                count_created += 1
            else:
                count_updated += 1
        
        logger.info(f"Successfully processed countries data: {count_created} created, {count_updated} updated")
        return {
            'created': count_created,
            'updated': count_updated,
            'total': count_created + count_updated
        }
        
    except requests.RequestException as e:
        logger.error(f"Error fetching countries data: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error processing countries data: {str(e)}")
        raise