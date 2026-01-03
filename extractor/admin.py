from django.contrib import admin
from django.db.models import Min, Max
from .models import (Country, Group, League, Season, Venue, BetParameter,
                     Team, Fixture, Odds, BookMaker, Bet, OddValues)
from import_export.admin import ImportExportModelAdmin
from .resources import (CountryResource, LeagueResource, SeasonResource,
                       TeamResource, FixtureResource, OddsResource, OddValuesResource)



@admin.register(Country)
class CountryAdmin(ImportExportModelAdmin):
    resource_classes = [CountryResource]
    list_display = ['code', 'name', 'sync_on']
    list_filter = ['name', 'sync_on']
    search_fields = ['name']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']
    search_fields = ['name']


@admin.register(League)
class LeagueAdmin(ImportExportModelAdmin):
    resource_classes = [LeagueResource]
    list_display = ['id', 'country_name', 'name', 'type', 'sync_on']
    list_filter = ['country__name', 'type', 'sync_on']
    search_fields = ['name']

    @admin.display
    def country_name(self, obj):
        return obj.country.name


@admin.action(description="sync on  selected seasons")
def sync_current(modeladmin, request, queryset):
    queryset.filter(current=True).update(sync_on=True)
    queryset.filter(current=False).update(sync_on=False)


@admin.register(Season)
class SeasonAdmin(ImportExportModelAdmin):
    actions = [sync_current]
    resource_classes = [SeasonResource]
    list_display = ['id', 'year', 'current', 'sync_on']
    list_filter = ['year', 'current', 'sync_on']


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    pass


@admin.register(Team)
class TeamAdmin(ImportExportModelAdmin):
    resource_classes = [TeamResource]
    list_display = ['id', 'name', 'country_name']
    list_filter = ['country__name']
    search_fields = ['name', 'country__name']

    @admin.display(description='country_name')
    def country_name(self, obj):
        return f'{obj.country.code} - {obj.country.name}'


@admin.register(BookMaker)
class BookMakerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'sync_on']


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'sync_on']


@admin.register(Fixture)
class FixtureAdmin(ImportExportModelAdmin):
    resource_classes = [FixtureResource]
    list_display = ['id', 'date', 'country_name', 'home_name', 'away_name',
                    'periods', 'status', 'league_name', 'home_goals', 'away_goals']
    list_filter = ['date', 'season__league__country__name']
    search_fields = ['date', 'home_name', 'away_name', 'league_name']

    @admin.display
    def home_name(self, obj):
        return f'{obj.home_team.name}' if obj.home_team else ''

    @admin.display
    def away_name(self, obj):
        return f'{obj.away_team.name}' if obj.away_team else ''

    @admin.display
    def league_name(self, obj):
        return f'{obj.season.league.id} - {obj.season.league.name}'

    @admin.display
    def country_name(self, obj):
        return f'{obj.season.league.country.code} - {obj.season.league.country.name}'


@admin.register(Odds)
class OddsAdmin(ImportExportModelAdmin):
    resource_classes = [OddsResource]
    list_display = ['bookmaker', 'bet', 'fixture']


@admin.register(OddValues)
class OddValuesAdmin(ImportExportModelAdmin):
    resource_classes = [OddValuesResource]
    list_display = ['odd__bookmaker', 'odd__bet', 'odd__fixture', 'odd__fixture__date', 'key', 'value']


@admin.register(BetParameter)
class BetParameterAdmin(admin.ModelAdmin):
    list_display = ['bet__name', 'key', 'prob_name']