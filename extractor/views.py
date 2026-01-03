from django.shortcuts import render
from django.http.response import HttpResponse
from .tasks import sync_countries, sync_leagues, sync_teams, sync_fixtures, sync_odds
from extractor.poisson_f import poisson_model, kelly_function
from extractor.models import Stats
from datetime import datetime, timedelta, timezone
import pandas as pd
from pretty_html_table import build_table
from random import random

def kelly_fn(x, odd=1, factor = 0.5):
    kelly = (x * (odd + 1) - 1) / odd * factor
    return kelly if kelly > 0 else 0


def sync(request):
    sync_countries()
    sync_leagues()
    sync_teams()
    sync_fixtures()
    sync_odds()
    return render(request, 'sync.html')


def probs_view(request, kelly: bool = False):
    results = poisson_model((datetime(2020, 1, 1, tzinfo=timezone.utc), datetime(2030, 1, 1, tzinfo=timezone.utc)))
    stats = Stats.objects.filter(fixture__in=results)
    stats_df = pd.DataFrame.from_records(stats.values())
    records = results.values(
        'id', 'date',
        'country', 'season__league__name', 'season__year',
        'home_team__name', 'away_team__name',
        'home_goals', 'away_goals',
        'home_favor_goals_avg', 'home_against_goals_avg',
        'away_favor_goals_avg', 'away_against_goals_avg',
        'home_league_goals_avg', 'away_league_goals_avg',
        'home_n', 'away_n', 'league_n',
        'l_attack', 'l_defense', 'v_attack', 'v_defense',
        'l_expected', 'v_expected',
        'l0', 'l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'l_over',
        'v0', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v_over',
        'al0', 'al1', 'al2', 'al3', 'al4', 'al5', 'al6', 'al7', 'al8',
        'av0', 'av1', 'av2', 'av3', 'av4', 'av5', 'av6', 'av7', 'av8',
        'win', 'lose', 'draw',
        'l_15', 'l_25', 'l_35', 'l_45', 'l_55', 'l_65', 'l_75', 'l_85',
        'v_15', 'v_25', 'v_35', 'v_45', 'v_55', 'v_65', 'v_75', 'v_85',
        )
    df = pd.DataFrame.from_records(records).rename(columns={
        'season__league__name': 'league',
        'season__year': 'season',
        'home_team__name': 'home',
        'away_team__name': 'away',
        'home_favor_goals_avg': 'home favor goals',
        'home_against_goals_avg': 'home against goals',
        'away_favor_goals_avg': 'away favor goals',
        'away_against_goals_avg': 'away against goals',
        'home_league_goals_avg': 'home league goals',
        'away_league_goals_avg': 'away league goals',
        'l_attack': 'attack (home)',
        'l_defense': 'defense (home)',
        'v_attack': 'attack (away)',
        'v_defense': 'defense (away)',
        'l_expected': 'local expected goals',
        'v_expected': 'away expected goals'
        })
    prob_columns = [
        'l0', 'l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'l_over',
        'v0', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v_over',
        'al0', 'al1', 'al2', 'al3', 'al4', 'al5', 'al6', 'al7', 'al8',
        'av0', 'av1', 'av2', 'av3', 'av4', 'av5', 'av6', 'av7', 'av8',
        'win', 'lose', 'draw',
        'l_15', 'l_25', 'l_35', 'l_45', 'l_55', 'l_65', 'l_75', 'l_85',
        'v_15', 'v_25', 'v_35', 'v_45', 'v_55', 'v_65', 'v_75', 'v_85',
        ]
    if kelly:
        for col in prob_columns:
            df[col] = df[col].apply(kelly_fn)
    if not stats_df.empty:
        df = df.merge(stats_df, left_on='id', right_on='fixture_id', how='left', suffixes=('', '_stats'))
    html_table = df.sort_values('date', ascending=False).to_html( index=False)
    return render(request, 'probs.html', context={
        'table': html_table
        })


def kelly_view(request):
    results = kelly_function(bookmaker=32, date_filter=(datetime(2020,1,1), datetime(2030,1,1)), only_positives=False)
    df = pd.DataFrame.from_records(results.values())
    return render(request, 'probs.html', context={'table': df.to_html()})


def push_button(request):
    results = kelly_function(bookmaker=32, date_filter=(datetime(2020,1,1), datetime(2030,1,1)))
    df = pd.DataFrame.from_records(results.values())
    dg = pd.DataFrame(columns=df.columns)
    while dg.kelly.sum() < 1.:
        df.loc[:, 'k0'] = df.kelly.cumsum() / df.kelly.sum()
        df.loc[:, 'k1'] = df.k0.shift(fill_value=0)
        r = random()
        row = df.loc[(df.k1 < r) & (df.k0 >= r), :]
        dg = pd.concat((dg, row))
        df.drop(index=row.index, inplace=True)
        df.drop(index=df.loc[df.kelly > 1 - dg.kelly.sum(), :].index)

    output = dg[['id', 'kelly']]
    output['kelly'] = output.kelly / output.kelly.sum() * 100
    return render(request, 'button.html', context={'table': output.to_html()})


def save_fixtures(request):
    kelly_results = kelly_function(bookmaker=32, date_filter=(datetime(2020,1,1), datetime(2030,1,1)), only_positives=False, list_all=True)
    df_kelly = pd.DataFrame.from_records(kelly_results.values())
    df_kelly.to_pickle('data/kelly.pkl')

    prob_results = poisson_model(date_filter=(datetime(2020,1,1), datetime(2030,1,1)), list_all=True)
    df_poisson = pd.DataFrame.from_records(prob_results.values())
    df_poisson.to_pickle('data/probs.pkl')
    return HttpResponse('fixtures saved')
    
    
def render_widget(request):
    if request.GET:
        value = request.GET.get('bet', 10000)
        value = float(value) if value else 10000
    else:
        value= 10000
    start_date, end_date = datetime.now() - timedelta(7), datetime.now() + timedelta(15)
    results = kelly_function(date_filter=(start_date, end_date), kelly_factor=1 / 2)
    df = pd.DataFrame.from_records(results.values())
    dg = pd.DataFrame(columns=df.columns)
    while dg.kelly.sum() < 1. and not df.empty:
        df.loc[:, 'k0'] = df.kelly.cumsum() / df.kelly.sum()
        df.loc[:, 'k1'] = df.k0.shift(fill_value=0)
        r = random()
        row = df.loc[(df.k1 < r) & (df.k0 >= r), :]
        dg = pd.concat((dg, row)) if not dg.empty else pd.DataFrame(row)
        df.drop(index=row.index, inplace=True)
        df.drop(index=df.loc[df.kelly > 1 - dg.kelly.sum(), :].index)

    output = dg[['bookmaker', 'country', 'league', 'home', 'away', 'date', 'bet', 'key', 'kelly']]
    output.loc[:, ('date',)] = output.date.apply(lambda x: datetime.strftime(x, '%Y-%m-%d'))
    output.loc[:, ('valor apuesta',)] = (output.kelly / output.kelly.sum() * value).apply(lambda x: f"$ {x:,.0f}")
    output = output.drop(columns=['kelly'])
    return render(request, 'bets_portal.html', 
                  context={
                      'table': build_table(output, 'blue_dark',
                                           padding='10px', 
                                           odd_bg_color='#0f3460',
                                           even_color='#1a1a2e',
                                           border_bottom_color="#00ff88"), 
                      'value': value})
