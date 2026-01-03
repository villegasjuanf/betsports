from .api_extractor import ApiExtractor
from .api_mapper import mapper
from .api_loader import bulk_create_or_update
from extractor.models import (
    BetParameter, Country, League, Season, Team, Stats, Fixture,
    Venue, Fixture, BookMaker, Bet, Odds, OddValues)
from django.db.utils import IntegrityError
import logging

logger = logging.getLogger(__name__)

def calculate_avg(fixture):
    data = dict(
        home_favor_goals_avg=fixture.f_home_favor_goals_avg,
        home_against_goals_avg=fixture.f_home_against_goals_avg,
        away_favor_goals_avg=fixture.f_away_favor_goals_avg,
        away_against_goals_avg=fixture.f_away_against_goals_avg,
        home_league_goals_avg=fixture.f_home_league_goals_avg,
        away_league_goals_avg=fixture.f_away_league_goals_avg,
        home_n=fixture.f_home_n,
        away_n=fixture.f_away_n,
        league_n=fixture.f_league_n,
    )
    Fixture.objects.filter(id=fixture.id).update(**data)


class ApiFootball:

    def __init__(self):
        self.api = ApiExtractor()

    def get_countries(self):
        response = self.api.get_countries()
        models = [mapper(Country, data) for data in response.get('response', [])]
        return {'country': bulk_create_or_update(Country, models)}

    def get_leagues(self, country_code):
        response = self.api.get_leagues(country_code)
        league_models = []
        season_models = []
        for league_ in response.get('response', []):
            league_models.append(mapper(League, league_))
            season_league_models = []
            for season_ in league_['seasons']:
                season_model = mapper(Season, season_,
                                      id=f'{league_["league"]["id"]}-{season_["year"]}')
                season_model.league = league_models[-1]
                season_league_models.append(season_model)

            season_models.extend(season_league_models)
        return {'league': bulk_create_or_update(League, league_models),
                'season': bulk_create_or_update(Season, season_models)}

    def get_teams(self, league):
        season = Season.objects.filter(league=league, current=True).first()
        response = self.api.get_teams(league, season.year)
        for data in response.get('response', []):
            model = mapper(Venue, data)
            try:
                model.save()
                venue = {'venue': Venue.objects.get(id=data['venue']['id'])}
            except IntegrityError as e:
                venue = {}
                logger.error(f"Error saving Venue: {e}")
            team_models = [mapper(Team, data, **venue)
                           for data in response.get('response', [])]
        return {'team': bulk_create_or_update(Team, team_models)}

    def get_fixtures(self, league):
        season = Season.objects.filter(league=league, current=True).first()
        response = self.api.get_fixtures(league, season.year)
        models = []
        for data in response.get('response', []):
            model = mapper(Fixture, data)
            model.season = Season.objects.get(id=f'{data["league"]["id"]}-{season.year}')
            models.append(model)
            
        return bulk_create_or_update(
            Fixture, models,
            ['date', 'status', 'periods', 'score', 'home_goals', 'away_goals'])

    def get_fixture_stats(self, league):

        fixtures = Fixture.objects.filter(
            season__league=league,
            season__current=True,
            stats__isnull=True,
            home_goals__isnull=False,
            away_goals__isnull=False
            )
        models = []
        for fixture in fixtures:
            home_team = fixture.home_team.id
            response_ = self.api.get_fixture_stats(fixture.id).get('response', {})
            if response_:
                response_ = {x['team']['id']: x['statistics'] for x in response_}
                response = {'home': {}, 'away': {}}
                for team, stats in response_.items():
                    team = 'home' if int(team) == home_team else 'away'
                    response[team] = {stat['type']: stat['value'] for stat in stats}
                model = Stats(
                    fixture=fixture,
                    home_shots_on_goal=response['home'].get("Shots on Goal"),
                    away_shots_on_goal=response['away'].get("Shots on Goal"),
                    home_shots_off_goal=response['home'].get("Shots off Goal"),
                    away_shots_off_goal=response['away'].get("Shots off Goal"),
                    home_total_shots=response['home'].get("Total Shots"),
                    away_total_shots=response['away'].get("Total Shots"),
                    home_blocked_shots=response['home'].get("Blocked Shots"),
                    away_blocked_shots=response['away'].get("Blocked Shots" ),
                    home_shots_inside_box=response['home'].get("Shots insidebox"),
                    away_shots_inside_box=response['away'].get("Shots insidebox"),
                    home_shots_outside_box=response['home'].get("Shots outsidebox"),
                    away_shots_outside_box=response['away'].get("Shots outsidebox"),
                    home_fouls=response['home'].get("Fouls"),
                    away_fouls=response['away'].get("Fouls"),
                    home_corners=response['home'].get("Corner Kicks"),
                    away_corners=response['away'].get("Corner Kicks"),
                    home_offsides=response['home'].get("Offsides"),
                    away_offsides=response['away'].get("Offsides"),
                    home_yellow_cards=response['home'].get("Yellow Cards"),
                    away_yellow_cards=response['away'].get("Yellow Cards"),
                    home_red_cards=response['home'].get("Red Cards"),
                    away_red_cards=response['away'].get("Red Cards"),
                    home_ball_possession=float(response['home'].get("Ball Possession", '').replace('%', '')) / 100\
                        if response['home'].get("Ball Possession") else None,
                    away_ball_possession=float(response['away'].get("Ball Possession", '').replace('%', '')) / 100\
                        if response['away'].get("Ball Possession") else None,
                    home_goalkeeper_saves=response['home'].get("Goalkeeper Saves"),
                    away_goalkeeper_saves=response['away'].get("Goalkeeper Saves"),
                    home_total_passes=response['home'].get("Total Passes"),
                    away_total_passes=response['away'].get("Total Passes"),
                    home_passes_accurate=response['home'].get("Passes accurate"),
                    away_passes_accurate=response['away'].get("Passes accurate")
                )
                models.append(model)
        return bulk_create_or_update(Stats, models)


    def get_odds(self, league, season, bookmaker):
        season = int(season.split('-')[-1])
        response = self.api.get_odds(league, season, bookmaker)['response']
        bet_catalog = BetParameter.objects.all()

        for fixture in response:
            for bookmaker in fixture['bookmakers']:
                for bet in bookmaker['bets']:
                    odd = Odds(
                        id=f'{bookmaker["id"]}-{bet["id"]}-{fixture["fixture"]["id"]}',
                        bookmaker=BookMaker.objects.get(id=bookmaker['id']),
                        bet=Bet.objects.get(id=bet['id']),
                        fixture=Fixture.objects.get(id=fixture['fixture']['id'])
                        )
                    if odd.bookmaker and odd.bet and odd.fixture:
                        try:
                            odd.save()
                        except IntegrityError as e:
                            logger.warning(e)
                        for value in bet['values']:
                            prob_name = bet_catalog.filter(bet=odd.bet, key=value['value']).first().prob_name\
                                if bet_catalog.filter(bet=odd.bet, key=value['value']).exists() else ''
                            odd_value = OddValues(
                                id=f'{odd}-{value["value"]}',
                                odd=odd,
                                key=value['value'],
                                value=value['odd'],
                                prob_name=prob_name
                                )
                            try:
                                odd_value.save()
                            except IntegrityError as e:
                                logger.warning(e)

    def get_bets(self):
        response = self.api.get_bets()['response']
        models = [mapper(Bet, data) for data in response if data['name'] is not None]
        return bulk_create_or_update(Bet, models)

    def get_bookmakers(self):
        response = self.api.get_bookmakers()['response']
        models = [mapper(BookMaker, data) for data in response if data['name'] is not None]
        return bulk_create_or_update(BookMaker, models)
