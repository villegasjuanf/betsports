import pytest
from datetime import datetime, timedelta
from extractor.apifootball.api_mapper import mapper
from extractor.models import Odds, Fixture, BookMaker, Bet


class TestOdds:

    def test_odds_extractor(self, extractor):
        response = extractor.get_odds(league=239, season=2025, bookmaker=32)
        assert response['results'] > 0

    @pytest.mark.django_db
    def test_odds_mapper(self, bet, bookmaker, fixture):
        data = {'id': 3,
                'values': [
                    {'value': 'Home', 'odd': '1.72'},
                    {'value': 'Draw', 'odd': '3.45'},
                    {'value': 'Away', 'odd': '5.00'}
                    ], 
                'bookmaker': 32,
                'fixture': 1489365}
        mapped = mapper(Odds, data)
        assert mapped
        assert isinstance(mapped.fixture, Fixture)
        assert isinstance(mapped.bet, Bet)
        assert isinstance(mapped.bookmaker, BookMaker)

    @pytest.mark.django_db
    def test_odds_api(self, bet, bookmaker, fixture, apifootball):
        response = apifootball.get_odds(league=239, season=2025, bookmaker=32)
        assert response


class TestBookmaker:

    def test_bookmakers(self, extractor):
        response = extractor.get_bookmakers(id=32)
        assert response['results'] == 1

    def test_all_bookmakers(self, extractor):
        response = extractor.get_bookmakers()
        assert response['results'] > 1

    @pytest.mark.django_db
    def test_create_bookmakers(self, apifootball):
        response = apifootball.get_bookmakers()
        assert response['create'] > 1 or response['update'] > 1


class TestBets:

    def test_all_bets(self, extractor):
        response = extractor.get_bets()
        assert response['results'] > 1

    @pytest.mark.django_db
    def test_create_bookmakers(self, apifootball):
        response = apifootball.get_bets()
        assert response['create'] > 1 or response['update'] > 1
