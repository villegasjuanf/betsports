import pytest
from datetime import datetime, timedelta

class TestApiFootball:

    def test_get(self, extractor):
        response = extractor.get('countries')
        assert response.status_code == 200
        assert extractor.ok

    @pytest.mark.skip(reason='Not required')
    def test_post(self, extractor):
        response = extractor.post('countries')
        assert response.status_code == 200
        assert extractor.ok


class TestCountries:

    def test_get_countries(self, extractor):
        response = extractor.get_countries()
        assert response.get('results') == 171
        assert response['errors'] == []


class TestLeagues:

    def test_get_leagues(self, extractor):
        response = extractor.get_leagues('CO')
        assert response.get('results') == 5
        assert response['errors'] == []


class TestFixtures:

    def test_get_fixtures(self, extractor):
        response = extractor.get_fixtures(239, 2020)
        assert response.get('results') == 233
        assert response['errors'] == []


class TestOdds:

    def test_get_odds(self, extractor):
        response = extractor.get_odds(239, 2025, datetime.now() - timedelta(days=0))
        assert response['errors'] == []

    def test_mapping(self, extractor):
        response = extractor.get_mapping()
        assert response['errors'] == []

    def test_bookmakers(self, extractor):
        response = extractor.get_bookmakers()
        assert response['errors'] == []

    def test_bets(self, extractor):
        response = extractor.get_bets()
        assert response['errors'] == []
