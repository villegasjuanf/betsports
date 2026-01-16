from extractor.models import (BookMaker, Country, League, Fixture,
                              OddValues, Season, Bet, BetParameter)
from extractor.apifootball.api_etl import ApiFootball, calculate_avg
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def sync_countries():
    api = ApiFootball()
    response = api.get_countries()
    logger.info(api.api.request_counter)
    return response


@shared_task
def sync_leagues():
    api = ApiFootball()
    for country in Country.objects.filter(sync_on=True).values_list('code', flat=True):
        api.get_leagues(country)

    logger.info(api.api.request_counter)
    Season.objects.filter(current=True).update(sync_on=True)


@shared_task
def sync_teams():
    api = ApiFootball()
    for league in League.objects.filter(sync_on=True).values_list('id', flat=True):
        api.get_teams(league)
    logger.info(api.api.request_counter)


@shared_task
def sync_fixtures(sync_stats=False):
    api = ApiFootball()
    saved = None
    for league in League.objects.filter(sync_on=True).values_list('id', flat=True):
        saved = api.get_fixtures(league)
        for fixture in Fixture.objects.filter(season__league=league):
            calculate_avg(fixture)
        if sync_stats:
            api.get_fixture_stats(league)
    logger.info(api.api.request_counter)
    return saved


@shared_task
def sync_odds():
    api = ApiFootball()
    api.get_bookmakers()
    api.get_bets()
    for season, league in Season.objects.select_related('league').filter(sync_on=True, league__sync_on=True).values_list('id', 'league__id'):
        for bookmaker in BookMaker.objects.filter(sync_on=True).values_list('id', flat=True):
            api.get_odds(league, season, bookmaker)
    logger.info(api.api.request_counter)


@shared_task
def sync_bet_catalog():
    params = OddValues.objects.filter(odd__bet__sync_on=True).values('key', 'odd__bet').distinct()
    for param in params:
        bet = Bet.objects.get(id=param['odd__bet'])
        BetParameter.objects.get_or_create(
            id=f'{bet.id}-{param["key"]}',
            key=param["key"],
            bet=bet
            )

