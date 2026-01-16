from typing import Tuple
from .models import BetParameter, Fixture, OddValues
from django.db.models.functions import Exp, Power, Coalesce, NullIf, Sign, Floor
from math import factorial
from django.db.models import F, Q, Case, When
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

INPLAY_STATUS = ('TBD', 'NS', '1H', '2H', 'HT', 'ET', 'BT', 'P', 'SUSP', 'INT', 'LIVE')

def fixture_qry(date_filter: datetime | Tuple[datetime, datetime] | None = None,
                  league: int | None = None, overall: bool = False,
                  list_all: bool = False):
    l_attack = Coalesce(F('home_favor_goals_avg')
                        / NullIf(F('home_league_goals_avg'), 0.), 0.)
    l_defense = Coalesce(F('home_against_goals_avg')
                         / NullIf(F('home_league_goals_avg'), 0.), 0.)
    v_attack = Coalesce(F('away_favor_goals_avg')
                        / NullIf(F('away_league_goals_avg'), 0.), 0.)
    v_defense = Coalesce(F('away_against_goals_avg')
                         / NullIf(F('away_league_goals_avg'), 0.), 0.)

    if isinstance(date_filter, datetime) and not list_all:
        fixtures = Fixture.objects.filter(date=date_filter)
    elif isinstance(date_filter, tuple) and not list_all:
        fixtures = Fixture.objects.filter(date__gte=date_filter[0],
                                          date__lt=date_filter[1] + timedelta(1))
    elif list_all:
        fixtures = Fixture.objects.all()
    else:
        fixtures = Fixture.objects.filter(date__gte=datetime.now(),
                                          date__lt=datetime.now() + timedelta(8)
                                          )
    if not list_all:
        fixtures = fixtures.filter(status__short__in=INPLAY_STATUS)
    if league:
        fixtures = fixtures.filter(season__league__id=league)
    else:
        fixtures = fixtures.filter(season__league__sync_on=True)

    fixtures = fixtures.exclude(Q(home_team__isnull=True) | Q(away_team__isnull=True))

    if overall:
        l_factor = (NullIf(F('home_league_goals_avg'), 0.) +
                    NullIf(F('away_league_goals_avg'), 0.)) / 2
        v_factor = (NullIf(F('home_league_goals_avg'), 0.) +
                    NullIf(F('away_league_goals_avg'), 0.)) / 2
    else:
        l_factor = F('home_league_goals_avg')
        v_factor = F('away_league_goals_avg')

    expected = fixtures.annotate(
        country=F('season__league__country__name'),
        l_attack=l_attack, l_defense=l_defense,
        v_attack=v_attack, v_defense=v_defense,
        l_expected=l_attack * v_defense * l_factor,
        v_expected=v_attack * l_defense * v_factor,
        )
    return expected.filter(home_n__gte=3, away_n__gte=3, league_n__gte=5)

def bookmaker_fixture_qry(date_filter: datetime | Tuple[datetime, datetime] | None = None,
                  league: int | None = None, overall: bool = False, bookmaker: int | None = None,
                  list_all: bool = False):
    l_attack = Coalesce(F('odd__fixture__home_favor_goals_avg')
                        / NullIf(F('odd__fixture__home_league_goals_avg'), 0.), 0.)
    l_defense = Coalesce(F('odd__fixture__home_against_goals_avg')
                         / NullIf(F('odd__fixture__home_league_goals_avg'), 0.), 0.)
    v_attack = Coalesce(F('odd__fixture__away_favor_goals_avg')
                        / NullIf(F('odd__fixture__away_league_goals_avg'), 0.), 0.)
    v_defense = Coalesce(F('odd__fixture__away_against_goals_avg')
                         / NullIf(F('odd__fixture__away_league_goals_avg'), 0.), 0.)

    base_query = OddValues.objects\
        .exclude(Q(prob_name='') | Q(odd__fixture__home_team__isnull=True) | Q(odd__fixture__away_team__isnull=True))

    if bookmaker:
        base_query = base_query.filter(odd__bookmaker__id=bookmaker)

    if isinstance(date_filter, datetime) and not list_all:
        fixtures = base_query.select_related('odd__fixture').filter(odd__fixture__date=date_filter)
    elif isinstance(date_filter, tuple) and not list_all:
        fixtures = base_query.select_related('odd__fixture').filter(odd__fixture__date__gte=date_filter[0],
                                          odd__fixture__date__lt=date_filter[1] + timedelta(1))
    elif list_all:
        fixtures = base_query.select_related('odd__fixture')
    else:
        fixtures = base_query.select_related('odd__fixture').filter(odd__fixture__date__gte=datetime.now(),
                                          odd__fixture__date__lt=datetime.now() + timedelta(8)
                                          )
    if league:
        fixtures = fixtures.filter(odd__fixture__season__league__id=league)
    else:
        fixtures = fixtures.filter(odd__fixture__season__league__sync_on=True)

    if  not list_all:
        fixtures = fixtures.filter(odd__fixture__status__short__in=INPLAY_STATUS)
    if overall:
        l_factor = (NullIf(F('odd__fixture__home_league_goals_avg'), 0.) +
                    NullIf(F('odd__fixture__away_league_goals_avg'), 0.)) / 2
        v_factor = (NullIf(F('odd__fixture__home_league_goals_avg'), 0.) +
                    NullIf(F('odd__fixture__away_league_goals_avg'), 0.)) / 2
    else:
        l_factor = F('odd__fixture__home_league_goals_avg')
        v_factor = F('odd__fixture__away_league_goals_avg')

    expected = fixtures.annotate(
        bookmaker=F('odd__bookmaker__name'),
        country=F('odd__fixture__season__league__country__name'),
        league=F('odd__fixture__season__league__name'),
        home=F('odd__fixture__home_team__name'),
        away=F('odd__fixture__away_team__name'),
        bet=F('odd__bet__name'),
        l_attack=l_attack, l_defense=l_defense,
        v_attack=v_attack, v_defense=v_defense,
        l_expected=l_attack * v_defense * l_factor,
        v_expected=v_attack * l_defense * v_factor,
        date=F('odd__fixture__date'),
        venue=F('odd__fixture__venue'),
        periods=F('odd__fixture__periods'),
        status=F('odd__fixture__status'),
        season=F('odd__fixture__season'),
        home_team=F('odd__fixture__home_team'),
        away_team=F('odd__fixture__away_team'),
        score=F('odd__fixture__score'),
        home_favor_goals_avg=F('odd__fixture__home_favor_goals_avg'),
        home_against_goals_avg=F('odd__fixture__home_against_goals_avg'),
        away_favor_goals_avg=F('odd__fixture__away_favor_goals_avg'),
        away_against_goals_avg=F('odd__fixture__away_against_goals_avg'),
        home_league_goals_avg=F('odd__fixture__home_league_goals_avg'),
        away_league_goals_avg=F('odd__fixture__away_league_goals_avg'),
        home_n=F('odd__fixture__home_n'),
        away_n=F('odd__fixture__away_n'),
        league_n=F('odd__fixture__league_n'),
        threshold=F('odd__bet__betparameter__threshold'),
        bet_pname=F('odd__bet__betparameter__prob_name'),
        )

    return expected.filter(home_n__gte=3, away_n__gte=3, league_n__gte=5)


def poisson_model(date_filter: datetime | Tuple[datetime, datetime] | None = None,
                  league: int | None = None, overall: bool = False,
                  bookmaker: int | None = None, list_all: bool = False, kelly: bool = False):

    def poisson_pdf(l_: str, k_: int):
        return Power(F(l_), k_) * Exp(-F(l_)) / factorial(k_)

    if bookmaker:
        expected = bookmaker_fixture_qry(date_filter, league, overall, bookmaker, list_all=list_all)
    elif not bookmaker and kelly:
        expected = bookmaker_fixture_qry(date_filter, league, overall, list_all=list_all)
    else:
        expected = fixture_qry(date_filter, league, overall, list_all=list_all)

    expected = expected.annotate(
        l0=poisson_pdf('l_expected', 0), v0=poisson_pdf('v_expected', 0),
        l1=poisson_pdf('l_expected', 1), v1=poisson_pdf('v_expected', 1),
        l2=poisson_pdf('l_expected', 2), v2=poisson_pdf('v_expected', 2),
        l3=poisson_pdf('l_expected', 3), v3=poisson_pdf('v_expected', 3),
        l4=poisson_pdf('l_expected', 4), v4=poisson_pdf('v_expected', 4),
        l5=poisson_pdf('l_expected', 5), v5=poisson_pdf('v_expected', 5),
        l6=poisson_pdf('l_expected', 6), v6=poisson_pdf('v_expected', 6),
        l7=poisson_pdf('l_expected', 7), v7=poisson_pdf('v_expected', 7),
        l8=poisson_pdf('l_expected', 8), v8=poisson_pdf('v_expected', 8),
        )
    expected = expected.annotate(
        l_over=1 - (F('l0') + F('l1') + F('l2') + F('l3') +
                    F('l4') + F('l5') + F('l6') + F('l7') + F('l8')),
        v_over=1 - (F('v0') + F('v1') + F('v2') + F('v3') +
                    F('v4') + F('v5') + F('v6') + F('v7') + F('v8')))
    expected = expected.annotate(
        al0=F('l0'),
        al1=F('l0') + F('l1'),
        al2=F('l0') + F('l1') + F('l2'),
        al3=F('l0') + F('l1') + F('l2') + F('l3'),
        al4=F('l0') + F('l1') + F('l2') + F('l3') + F('l4'),
        al5=F('l0') + F('l1') + F('l2') + F('l3') + F('l4') + F('l5'),
        al6=F('l0') + F('l1') + F('l2') + F('l3') + F('l4') + F('l5') + F('l6'),
        al7=F('l0') + F('l1') + F('l2') + F('l3') + F('l4') + F('l5') + F('l6') + F('l7'),
        al8=F('l0') + F('l1') + F('l2') + F('l3') + F('l4') + F('l5') + F('l6') + F('l7') + F('l8'),
        av0=F('v0'),
        av1=F('v0') + F('v1'),
        av2=F('v0') + F('v1') + F('v2'),
        av3=F('v0') + F('v1') + F('v2') + F('v3'),
        av4=F('v0') + F('v1') + F('v2') + F('v3') + F('v4'),
        av5=F('v0') + F('v1') + F('v2') + F('v3') + F('v4') + F('v5'),
        av6=F('v0') + F('v1') + F('v2') + F('v3') + F('v4') + F('v5') + F('v6'),
        av7=F('v0') + F('v1') + F('v2') + F('v3') + F('v4') + F('v5') + F('v6') + F('v7'),
        av8=F('v0') + F('v1') + F('v2') + F('v3') + F('v4') + F('v5') + F('v6') + F('v7') + F('v8'),
        )
    expected = expected.annotate(
        win=F('l_over') * F('av8')
        + F('l8') * F('av7')
        + F('l7') * F('av6')
        + F('l6') * F('av5')
        + F('l5') * F('av4')
        + F('l4') * F('av3')
        + F('l3') * F('av2')
        + F('l2') * F('av1')
        + F('l1') * F('av0'),
        lose=F('v_over') * F('al8')
        + F('v8') * F('al7')
        + F('v7') * F('al6')
        + F('v6') * F('al5')
        + F('v5') * F('al4')
        + F('v4') * F('al3')
        + F('v3') * F('al2')
        + F('v2') * F('al1')
        + F('v1') * F('al0'),
        draw=F('l_over') * F('v_over')
        + F('l8') * F('v8')
        + F('l7') * F('v7')
        + F('l6') * F('v6')
        + F('l5') * F('v5')
        + F('l4') * F('v4')
        + F('l3') * F('v3')
        + F('l2') * F('v2')
        + F('l1') * F('v1')
        + F('l0') * F('v0'),
        l_15=1 - F('al1'), v_15=1 - F('av1'),
        l_25=1 - F('al2'), v_25=1 - F('av2'),
        l_35=1 - F('al3'), v_35=1 - F('av3'),
        l_45=1 - F('al4'), v_45=1 - F('av4'),
        l_55=1 - F('al5'), v_55=1 - F('av5'),
        l_65=1 - F('al6'), v_65=1 - F('av6'),
        l_75=1 - F('al7'), v_75=1 - F('av7'),
        l_85=1 - F('al8'), v_85=1 - F('av8'),
        o_05=1 - F('l0') * F('v0')
        )
    return expected.filter(Q(win__isnull=False) | Q(lose__isnull=False))

def kelly_function(bookmaker: int | None = None, league: int | None = None, overall: bool = False,
                date_filter: datetime | Tuple[datetime, datetime] | None = None,
                kelly_factor: float = 0.5, only_positives: bool = True, list_all: bool = False):
    expected = poisson_model(date_filter, league, overall, bookmaker, list_all=list_all, kelly=True)
    conditions = tuple(When(prob_name=par, then=F(par))
                    for par in BetParameter.objects.values_list('prob_name', flat=True))
    expected = expected.annotate(prob=Case(*conditions))
    logger.info(f'recovered {expected.count()} bets')
    expected = expected.filter(prob__gte=F('threshold'), prob_name=F('bet_pname'))
    logger.info(f'...and filtered {expected.count()} records with high probs')

    def kelly_fn(factor=1.):
        kelly = (F('prob') * (F('value') + 1) - 1) / F('value')
        return kelly * factor * Floor(.5 * (Sign(kelly) + 1))

    result = expected.annotate(
        kelly=kelly_fn(kelly_factor),
        flag=F('odd__fixture__season__league__country__flag'),
        home_badge=F('odd__fixture__home_team__logo'),
        away_badge=F('odd__fixture__away_team__logo')
        ).filter(kelly__isnull=False).order_by('-kelly')

    return result.filter(kelly__gt=0) if only_positives else result

