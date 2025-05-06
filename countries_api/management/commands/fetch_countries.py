
from django.core.management.base import BaseCommand
from countries_api.utils import fetch_and_store_countries

class Command(BaseCommand):
    help = 'Fetch countries data from the REST Countries API and store in the database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Fetching countries data...'))
        
        try:
            result = fetch_and_store_countries()
            self.stdout.write(self.style.SUCCESS(
                f"Successfully processed countries data: {result['created']} created, "
                f"{result['updated']} updated, {result['total']} total"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))