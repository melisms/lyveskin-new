

from .models import Item

def get_me_queryset(category):
    queryset = Item.objects.none()

    if category == 'sunscreen':
        queryset |= Item.objects.filter(category__name='Sunscreen')
    elif category == 'moisturizer':
        queryset |= Item.objects.filter(category__name='Moisturizer')
    elif category == 'cleanser':
        queryset |= Item.objects.filter(category__name='Cleanser')
    elif category == 'serum':
        queryset |= Item.objects.filter(category__name='Serum')
    elif category == 'mask':
        queryset |= Item.objects.filter(category__name='Mask')

    return queryset