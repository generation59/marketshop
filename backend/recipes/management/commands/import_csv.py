import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Import data from CSV files into the database'

    INGREDIENTS_CSV_PATH = 'data/ingredients.csv'
    TAGS_CSV_PATH = 'data/tags.csv'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ingredients-path', type=str, default=self.INGREDIENTS_CSV_PATH,
            help='Path to the ingredients CSV file'
        )
        parser.add_argument(
            '--tags-path', type=str, default=self.TAGS_CSV_PATH,
            help='Path to the tags CSV file'
        )

    def handle_ingredients(self, path):
        with open(path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            objs = [
                Ingredient(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
                for row in reader
            ]
            Ingredient.objects.bulk_create(objs)

    def handle_tags(self, path):
        with open(path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            objs = [
                Tag(
                    id=row['id'],
                    name=row['name'],
                    color=row['color'],
                    slug=row['slug'],
                )
                for row in reader
            ]
            Tag.objects.bulk_create(objs)

    def handle(self, *args, **kwargs):
        ingredients_path = kwargs.get('ingredients_path',
                                      self.INGREDIENTS_CSV_PATH)
        tags_path = kwargs.get('tags_path', self.TAGS_CSV_PATH)
        self.handle_tags(tags_path)
        self.handle_ingredients(ingredients_path)
