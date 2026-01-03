import os
import requests
import logging
import time
from datetime import datetime


logger = logging.getLogger(__name__)


class ApiExtractor:
    sleep = 0.5

    def __init__(self) -> None:
        self.headers = {
            'x-rapidapi-host': os.environ.get('API_FOOTBALL_HOST'),
            'x-rapidapi-key': os.environ.get('API_FOOTBALL_KEY')
            }
        self.url_base = os.environ.get('API_FOOTBALL_URL')
        self.errors = []
        self.response = None
        self.ok = None

    def get(self, api: str, **kwargs):
        url = f'{self.url_base}{api}'
        self.response = requests.get(url, headers=self.headers, params=kwargs)
        self.ok = self.response.status_code < 400

        if self.response.status_code >= 400:
            logger.error(f'resquest to {url} returns {self.response.status_code}')

        time.sleep(self.sleep)
        if 'errors' in self.response.json().keys():
            self.errors.extend(self.response.json().get('errors', []))

        return self.response

    def post(self, api: str, **kwargs):
        url = f'{self.url_base}{api}'
        self.response = requests.post(url, headers=self.headers, json=kwargs)
        self.ok = self.response.status_code < 400

        if self.response.status_code >= 400:
            logger.error(f'resquest to {url} returns {self.response.status_code}')
        time.sleep(self.sleep)
        if 'errors' in self.response.json().keys():
            self.errors.extend(self.response.json().get('errors').values())
        return self.response

    def __set_empty_pk(self, response, pk_field, secondary_field):
        data = response.get('response', [])
        empty_items = filter(lambda x: x.get(pk_field) is None, data)
        for item in empty_items:
            data.remove(item)
            item[pk_field] = item.get(secondary_field)
            data.append(item)
        response['response'] = data
        return response

    def get_countries(self, **kwargs):
        response = self.get('countries', **kwargs).json()
        return self.__set_empty_pk(response, 'code', 'name')

    def get_leagues(self, country_code: str, **kwargs):
        response = self.get('leagues', code=country_code, **kwargs).json()
        return response

    def get_teams(self, league: str, season: str, **kwargs):
        response = self.get('teams', league=league, season=season, **kwargs).json()
        return response

    def get_fixtures(self, league: int, season: int, **kwargs):
        response = self.get('fixtures', league=league, season=season, **kwargs).json()
        return response

    def get_fixture_stats(self, fixture: int):
        response = self.get('fixtures/statistics', fixture=fixture).json()
        return response

    def get_odds(self, league: int, season: int, bookmaker: int):
        response = self.get('odds', league=league, season=season,
                            bookmaker=bookmaker).json()
        return response

    def get_mapping(self, **kwargs):
        response = self.get('odds/mapping', **kwargs).json()
        return response

    def get_bookmakers(self, **kwargs):
        response = self.get('odds/bookmakers', **kwargs).json()
        return response

    def get_bets(self, **kwargs):
        response = self.get('odds/bets', **kwargs).json()
        return response
