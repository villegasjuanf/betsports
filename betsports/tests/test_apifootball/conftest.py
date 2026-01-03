from datetime import datetime
import pytest
from extractor.apifootball.api_extractor import ApiExtractor
from extractor.apifootball.api_etl import ApiFootball
from extractor.models import BookMaker, Bet, Fixture

@pytest.fixture
def bookmaker(request):
    bookmaker = BookMaker(
        id=32,
        name='bookmaker',
        sync_on=True
        )
    bookmaker.save()
    return BookMaker.objects.get(id=32)

@pytest.fixture
def fixture(request):
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
def bet(request):
    bet = Bet(
        id=3,
        name='bet'
        )
    bet.save()
    return Bet.objects.get(id=3)

@pytest.fixture
def extractor():
    return ApiExtractor()

@pytest.fixture
def apifootball(request):
    return ApiFootball()