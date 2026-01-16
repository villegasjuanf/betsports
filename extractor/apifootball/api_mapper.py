from django.db import models
from typing import Sequence, Any

MAPPING = {
    'Country': {
        'code': ['code'],
        'name': ['name'],
        'flag': ['flag'],
    },
    'League': {
        'id': ['league', 'id'],
        'name': ['league', 'name'],
        'type': ['league', 'type'],
        'logo': ['league', 'logo'],
        'country': {'code': ['country', 'code']},
    },
    'Season': {
        'id': ['id'],
        'year': ['year'],
        'start': ['start'],
        'end': ['end'],
        'current': ['current'],
        'coverage': ['coverage'],
    },
    'Team': {
        'id': ['team', 'id'],
        'name': ['team', 'name'],
        'code': ['team', 'code'],
        'country': {'name': ['team', 'country']},
        'founded': ['team', 'founded'],
        'national': ['team', 'national'],
        'logo': ['team', 'logo'],
        'venue': {'id': ['venue', 'id']},
        },
    'Venue': {
        'id': ['venue', 'id'],
        'name': ['venue', 'name'],
        'address': ['venue', 'address'],
        'city': ['venue', 'city'],
        'country': {'name': ['team', 'country']},
        'capacity': ['venue', 'capacity'],
        'surface': ['venue', 'surface'],
        'image': ['venue', 'image'],
    },
    'Fixture': {
        'id': ['fixture', 'id'],
        'date': ['fixture', 'date'],
        'venue': {'id': ['fixture', 'venue', 'id']},
        'periods': ['fixture', 'periods'],
        'status': ['fixture', 'status'],
        'score': ['fixture', 'score'],
        'home_team': {'id': ['teams', 'home', 'id']},
        'away_team': {'id': ['teams', 'away', 'id']},
        'home_goals': ['goals', 'home'],
        'away_goals': ['goals', 'away'],
    },
    'Stats': {
        'id': ['parameters', 'fixture'],
        'stats': ['statistics'],
    },
    'BookMaker': {
        'id': ['id'],
        'name': ['name'],
    },
    'Bet': {
        'id': ['id'],
        'name': ['name'],
    },
    'Odds': {
        'bookmaker': {'id': ['bookmaker']},
        'bet': {'id': ['id']},
        'odds': ['values'],
        'fixture': {'id': ['fixture']}
    }
}


def deep_get(data: dict, keys: Sequence, default: Any = None):
    if not data:
        return default
    inner = data.get(keys.pop(0), {}) if keys else {}
    return deep_get(inner, keys, default) if keys else inner


def mapper(model: models.Model, data: dict, **kwargs):
    mapper = MAPPING.get(model.__name__)
    mapped = {**kwargs}
    for k, v in mapper.items():
        field = model._meta.get_field(k)
        if field.many_to_one or field.one_to_many or field.many_to_many or field.one_to_one:
            assert isinstance(v, dict), f"{v} Related fields must be a dictionary"
            param_key, param = tuple(v.items())[0]
            param = deep_get(data, param.copy())
            mapped[k] = field.related_model.objects\
                .filter(**{param_key: param}).first()
        else:
            mapped[k] = deep_get(data, v.copy())
    obj = model(**mapped)
    return obj
