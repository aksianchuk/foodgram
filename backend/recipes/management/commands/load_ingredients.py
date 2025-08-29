import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Команда, которая позволяет загрузить ингредиенты из JSON файла в базу
    данных.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            required=True,
            help='Путь к файлу'
        )

    def handle(self, *args, **options):
        file_path = options['path']
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'Файл не найден: {file_path}')
            )
            return

        if Ingredient.objects.exists():
            self.stdout.write(self.style.WARNING('Ингредиенты уже загружены'))
            return

        with open(file_path, encoding='utf-8') as file:
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
