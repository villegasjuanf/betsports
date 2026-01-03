from django.db.models import Model
from typing import List
import logging

logger = logging.getLogger(__name__)


def bulk_create_or_update(model, data: List[Model], update_fields: List[str] | None = None,
                          batch_size: int = 100):
    update, create = {}, {}
    result = {}
    for item in data:
        if model.objects.filter(pk=item.pk).exists():
            update[item.pk] = item
        else:
            create[item.pk] = item
    result['create'] = len(model.objects.bulk_create(create.values(), batch_size=batch_size))
    if update_fields:
        result['update'] = model.objects.bulk_update(
            update.values(),
            update_fields, batch_size=batch_size)
    logger.info(f'{model.__name__}: {result}')
    return result
