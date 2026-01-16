from datetime import timedelta
from django.shortcuts import render
from extractor.models import Fixture
from django.utils.timezone import now
from extractor.poisson_f import kelly_function
import pandas as pd
from random import random


# Create your views here.
def main(request):
    return render(request, 'templates/main_single_panel.html')


def next_table(request):
    fixtures = Fixture.objects.filter(
        season__sync_on=True,
        season__league__sync_on=True,
        season__league__country__sync_on=True,
        status__short='NS',
        date__gte=now(),
        date__lte=now() + timedelta(4),
        home_team__isnull=False,
        away_team__isnull=False).order_by('season')
    return render(request, 'next_table.html', context={'fixtures': fixtures})

def bets_table(request):
    bet = request.GET.get('bet', 100000)
    results = kelly_function(
        date_filter=(now(), now() + timedelta(15)))
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

    output = dg[[
        'bookmaker', 'country', 'flag', 'league',
        'date', 'bet', 'key', 'value',
        'home', 'home_badge',
        'away', 'away_badge',
        'kelly']]
    output.loc[:, ('kelly',)] = output.kelly / output.kelly.sum() * bet
    output.loc[:, ('expected',)] = output.kelly * output.value
    total = output.expected.sum()
    return render(request, 'bets_table.html', context={'bets': output, 'total': total})