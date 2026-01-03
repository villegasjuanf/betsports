from extractor.models import Country
import pytest
from extractor.apifootball.api_loader import bulk_create_or_update


@pytest.fixture
def countries():
    yield [
        Country(code='US', name='United States', flag='us.png'),
        Country(code='CA', name='Canada', flag='ca.png')
        ]
    Country.objects.filter(name__in=['United States', 'Canada']).delete()


class TestCreateOrUpdate:

    @pytest.mark.django_db
    def test_create(self, countries):
        result = bulk_create_or_update(Country, countries, ['name'])
        assert result['create'] == len(countries)

    @pytest.mark.django_db
    def test_update(self, countries):
        countries[0].save()
        result = bulk_create_or_update(Country, countries, ['name'])
        assert result['update'] == 1
        assert result['create'] == len(countries[1:])
