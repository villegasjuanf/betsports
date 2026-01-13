from rest_framework import serializers
from extractor.models import Country, League, Team, Venue, Fixture, Odds, Bet, BookMaker, Season


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = '__all__'

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    class Meta:
        model = Team
        fields = '__all__'


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'


class FixtureSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer()
    away_team = TeamSerializer()
    venue = VenueSerializer()
    class Meta:
        model = Fixture
        fields = '__all__'


class OddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Odds
        fields = '__all__'


class BetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = '__all__'


class BookmakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookMaker
        fields = '__all__'
