from datetime import datetime
import pytest
from extractor.apifootball.api_extractor import ApiExtractor
from extractor.apifootball.api_etl import ApiFootball
from extractor.models import BookMaker, Bet, Fixture, UserConfig, User, Odds, OddValues


@pytest.fixture
def admin(admin_user):
    user = User.objects.get(username='admin')
    UserConfig.objects.create(user=user)
    return user

@pytest.fixture
def bookmaker():
    bookmaker = BookMaker(
        id=32,
        name='bookmaker',
        sync_on=True
        )
    bookmaker.save()
    return BookMaker.objects.get(id=32)

@pytest.fixture
def fixture():
    fixture = Fixture(
        id=1489365,
        date=datetime(2025, 12, 1),
        periods={},
        status={},
        score={}
        )
    fixture.save()
    return Fixture.objects.get(id=1489365)

@pytest.fixture
def bet():
    bet = Bet(
        id=3,
        name='bet'
        )
    bet.save()
    return Bet.objects.get(id=3)

@pytest.fixture
def odds(bookmaker, bet, fixture):
    odds = Odds(
        id='odd', bookmaker=bookmaker,
        bet=bet, fixture=fixture)
    odds.save()

    values = OddValues(
        id='values', odd=Odds.objects.get(id='odd'),
        key='home', value=10.)
    values.save()
    return OddValues.objects.get(id='values')

@pytest.fixture
def extractor():
    return ApiExtractor()

@pytest.fixture
def apifootball(request):
    return ApiFootball()