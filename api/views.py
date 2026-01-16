from rest_framework import viewsets
from api.serializers import (CountrySerializer, LeagueSerializer, FixtureSerializer, TeamSerializer,
                             OddSerializer, BookmakerSerializer, BetSerializer, UserBetsSerializer,
                             UserBetItemsSerializer)
from extractor.models import Country, League, Team, Fixture, Odds, BookMaker, Bet, UserBets, UserBetItems
from django.utils.timezone import now
from datetime import timedelta


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.filter(sync_on=True)
    serializer_class = CountrySerializer


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = League.objects.filter(sync_on=True)
    serializer_class = LeagueSerializer


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.filter(country__sync_on=True)
    serializer_class = TeamSerializer


class FixtureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Fixture.objects.filter(
        home_team__country__sync_on=True,
        away_team__country__sync_on=True,
        date__range=(now(), now() + timedelta(15)))
    serializer_class = FixtureSerializer


class OddViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Odds.objects.filter(bet__sync_on=True, bookmaker__sync_on=True)
    serializer_class = OddSerializer


class BookmakerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookMaker.objects.filter(sync_on=True)
    serializer_class = BookmakerSerializer


class BetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bet.objects.filter(sync_on=True)
    serializer_class = BetSerializer


class UsetBetsViewSet(viewsets.ModelViewSet):
    queryset = UserBets.objects.filter()
    serializer_class = UserBetsSerializer


class UsetBetItemsViewSet(viewsets.ModelViewSet):
    queryset = UserBetItems.objects.filter()
    serializer_class = UserBetItemsSerializer