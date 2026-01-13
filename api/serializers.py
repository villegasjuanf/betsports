from adrf import serializers
from extractor.models import Country, League, Team, Venue, Fixture, Odds, Bet, BookMaker


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
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
