from django.core.management.base import BaseCommand
from store.models import Product


class Command(BaseCommand):
    help = 'Seed 4 sample products for the storefront'

    def handle(self, *args, **kwargs):
        products = [
            {
                'name': 'Wireless Headphones',
                'description': 'Over-ear Bluetooth headphones with noise cancellation.',
                'price': 1999.00,
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e',
            },
            {
                'name': 'Smart Watch',
                'description': 'Fitness tracking smart watch with heart-rate monitor.',
                'price': 2999.00,
                'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30',
            },
            {
                'name': 'Backpack',
                'description': 'Water-resistant laptop backpack, 25L capacity.',
                'price': 1499.00,
                'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62',
            },
            {
                'name': 'Sunglasses',
                'description': 'UV-protection polarized sunglasses.',
                'price': 799.00,
                'image_url': 'https://images.unsplash.com/photo-1511499767150-a48a237f0083',
            },
        ]
        for p in products:
            obj, created = Product.objects.get_or_create(name=p['name'], defaults=p)
            status = 'created' if created else 'already exists'
            self.stdout.write(f"{p['name']}: {status}")
