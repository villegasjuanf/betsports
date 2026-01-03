from adrf import viewsets
from api.serializers import (CountrySerializer, LeagueSerializer, FixtureSerializer, TeamSerializer,
                             OddSerializer, BookmakerSerializer, BetSerializer)
from extractor.models import Country, League, Team, Fixture, Odds, BookMaker, Bet


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class FixtureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Fixture.objects.all()
    serializer_class = FixtureSerializer


class OddViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Odds.objects.all()
    serializer_class = OddSerializer


class BookmakerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookMaker.objects.all()
    serializer_class = BookmakerSerializer


class BetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bet.objects.all()
    serializer_class = BetSerializer
