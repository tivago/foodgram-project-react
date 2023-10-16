import json
import os

from django.core.management.base import BaseCommand

from foodgram.settings import DATA_FILES_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    """Загрузчик в БД из JSON файла."""

    def handle(self, *args, **options):
        file_name = 'ingredients.json'
        json_path = os.path.join(DATA_FILES_DIR, file_name)
        try:
            with open(json_path, 'rb') as file:
                data = json.load(file)
            for ingredient in data:
                obj, created = Ingredient.objects.get_or_create(
                    name=ingredient["name"],
                    measurement_unit=ingredient["measurement_unit"]
                )
                if not created:
                    print(
                        f'Ингридиент {ingredient["name"]} уже есть в базе')
            print('finished')
        except FileNotFoundError:
            print(f'Файл {file_name} не найден.')
            return
