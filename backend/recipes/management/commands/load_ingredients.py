import csv

from django.core.management.base import BaseCommand
from foodgram.settings import CSV_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    """Чтение файла CSV и создания экземпляров модели"""

    def handle(self, *args, **options):
        with open(
            f'{CSV_DIR}/ingredients.csv',
            encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in reader
            )
