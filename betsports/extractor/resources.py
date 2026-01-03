from import_export import resources
from .models import (Country, League, Season, Venue, BetParameter,
                     Team, Fixture, Odds, BookMaker, Bet, OddValues)

class CountryResource(resources.ModelResource):

    class Meta:
        model = Country


class LeagueResource(resources.ModelResource):

    class Meta:
        model = League


class SeasonResource(resources.ModelResource):

    class Meta:
        model = Season


class TeamResource(resources.ModelResource):

    class Meta:
        model = Team


class FixtureResource(resources.ModelResource):

    class Meta:
        model = Fixture


class OddsResource(resources.ModelResource):

    class Meta:
        model = Odds


class OddValuesResource(resources.ModelResource):

    class Meta:
        model = OddValues