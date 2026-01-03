import pytest
from extractor.apifootball.api_etl import ApiFootball
from extractor.models import Country, League, Team, Season, Venue, Fixture


@pytest.fixture
def api():
    return ApiFootball()


@pytest.fixture
def countries(api):
    yield api.get_countries()
    Country.objects.all().delete()


@pytest.fixture
def leagues(api, countries):
    yield api.get_leagues('CO')
    League.objects.all().delete()
    Season.objects.all().delete()


@pytest.fixture
def teams(api, leagues):
    yield api.get_teams(239)
    Team.objects.all().delete()
    Venue.objects.all().delete()


@pytest.fixture
def fixtures(api, teams):
    yield api.get_fixtures(239)
    Fixture.objects.all().delete()


class TestCountry:

    @pytest.mark.django_db
    def test_country(self, countries):
        assert Country.objects.count() == 170
        assert Country.objects.get(code='CO').name == 'Colombia'


class TestLeague:

    @pytest.mark.django_db
    def test_leagues(self, leagues):
        assert League.objects.count() == 5
        assert League.objects.get(id=239).name == 'Primera A'
        assert Season.objects.get(id='239-2021').year == 2021


class TestTeam:

    @pytest.mark.django_db
    def test_teams(self, teams):
        assert Team.objects.count() == 20
        assert Team.objects.get(id=1125).name == 'Millonarios'


class TestFixtures:

    @pytest.mark.django_db
    def test_fixtures(self, fixtures):
        assert Fixture.objects.count() > 0
