import pytest
from extractor.apifootball.api_mapper import deep_get, mapper
from extractor.models import Country, League, Season


class TestDeepGet:

    @pytest.fixture
    def nested_dict(self):
        return {
            'a': {'a1': 1, 'a2': 2},
            'b': {'b1': 3, 'b2': 4}
            }

    def test_deep_get(self, nested_dict):
        assert deep_get(nested_dict, ['a', 'a2']) == 2
        assert deep_get(nested_dict, ['b', 'b1']) == 3

    def test_defaults(self, nested_dict):
        assert deep_get(nested_dict, ['c', 'a2']) is None
        assert deep_get(nested_dict, ['c', 'a2'], 9999) == 9999


class TestMapper:

    @pytest.fixture
    def country_response(self):
        return {
            'response': {
                'code': 236,
                'name': 'colombia',
                'flag': 'http://',
                }
            }

    @pytest.fixture
    def league_response(self):
        return {
            'response': {
                'league': {
                    'id': 1,
                    'name': 'La Liga',
                    'type': 'Football',
                    'logo': 'http://',
                    },
                'season': {
                    'id': '2020',
                    'year': 2020,
                    'start': '2020-01-01',
                },
                'country': {
                    'code': 45,
                    'name': 'Spain',
                },
            }
        }

    @pytest.mark.django_db
    def test_country_mapping(self, country_response):
        model = mapper(Country, country_response)
        assert model.code == 236
        assert model.name == 'colombia'
        assert model.flag == 'http://'

    @pytest.mark.django_db
    def test_league_mapping(self, league_response):
        model = mapper(League, league_response)
        assert model.id == 1
        assert model.name == 'La Liga'
        assert model.type == 'Football'
        assert model.logo == 'http://'
        assert model.country_id is None

    @pytest.mark.django_db
    def test_season_mapping(self, league_response):
        model = mapper(Season, league_response)
        assert model.id == '2020'
        assert model.year == 2020
        assert model.start == '2020-01-01'
        assert model.league_id is None
