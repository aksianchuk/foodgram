import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


DEFAULT_JSON_PATH = os.path.join(
    os.path.dirname(settings.BASE_DIR),
    'data',
    'ingredients.json'
)


class Command(BaseCommand):
    """
    Команда, которая позволяет загрузить ингредиенты из JSON файла в базу
    данных.
    """

    def handle(self, *args, **options):
        if not os.path.exists(DEFAULT_JSON_PATH):
            self.stdout.write(
                self.style.ERROR(f'Файл не найден: {DEFAULT_JSON_PATH}')
            )
            return
        if Ingredient.objects.exists():
            self.stdout.write(self.style.WARNING('Ингредиенты уже загружены'))
            return

        with open(DEFAULT_JSON_PATH, encoding='utf-8') as file:
            data = json.load(file)
        ingredients = [
            Ingredient(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )
            for item in data
        ]
        Ingredient.objects.bulk_create(ingredients)
        self.stdout.write(
            self.style.SUCCESS(f'Загружено {len(ingredients)} ингредиентов')
        )
