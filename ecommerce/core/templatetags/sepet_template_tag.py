from django import template
from core.models import Siparis

register = template.Library()

@register.filter
def sepet_item_count(user):
    if user.is_authenticated:
        qs = Siparis.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
        return 0
