import os
from django.db import models
from django.db.models import Avg, Count, Max, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

AVERAGES_OVER_LAST_N_MATCHES = os.environ.get('AVERAGES_OVER_LAST_N_MATCHES', 10)

class UserConfig(models.Model):
    use_stats = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)




class Country(models.Model):
    code = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    flag = models.URLField(max_length=255, blank=True, null=True)
    sync_on = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Group(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class League(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, blank=True)
    logo = models.URLField(max_length=255, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    sync_on = models.BooleanField(default=False)
    group = models.ManyToManyField(Group)

    def __str__(self):
        return self.name


class Season(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    year = models.IntegerField()
    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)
    current = models.BooleanField(default=False)
    coverage = models.JSONField()
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    sync_on = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.league.name} - {self.year}'


class Venue(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    capacity = models.IntegerField(blank=True, null=True)
    surface = models.CharField(max_length=255, blank=True, null=True)
    image = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    founded = models.IntegerField(blank=True, null=True)
    national = models.BooleanField(default=False)
    logo = models.URLField(max_length=255, blank=True, null=True)
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class BookMaker(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    sync_on = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Bet(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    field = models.CharField(max_length=255, blank=True)
    sync_on = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class BetParameter(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    key = models.CharField(max_length=50)
    bet = models.ForeignKey(Bet, on_delete=models.CASCADE)
    prob_name = models.CharField(max_length=32, blank=True)
    threshold = models.FloatField(default=0)

@receiver(post_save, sender=BetParameter, dispatch_uid="update_prob_name")
def update_prob_name(sender, instance, **kwargs):
    OddValues.objects.filter(
        key=instance.key,
        odd__bet=instance.bet,
        ).update(prob_name=instance.prob_name)


class Fixture(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateTimeField()
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True)
    periods = models.JSONField()
    status = models.JSONField()
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True)
    home_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='home')
    away_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='away')
    home_goals = models.IntegerField(null=True)
    away_goals = models.IntegerField(null=True)
    score = models.JSONField()
    model_predictions = models.JSONField(default=dict, null=True)
    home_favor_goals_avg = models.FloatField(null=True)
    home_against_goals_avg = models.FloatField(null=True)
    away_favor_goals_avg = models.FloatField(null=True)
    away_against_goals_avg = models.FloatField(null=True)
    home_league_goals_avg = models.FloatField(null=True)
    away_league_goals_avg = models.FloatField(null=True)
    home_n = models.FloatField(null=True)
    away_n = models.FloatField(null=True)
    league_n = models.FloatField(null=True)

    def __str__(self):
        home_team_name = self.home_team.name if self.home_team else 'N/A'
        away_team_name = self.away_team.name if self.away_team else 'N/A'
        return f'{self.id} - {home_team_name} vs {away_team_name}'

    @property
    def f_home_favor_goals_avg(self):
        fixtures = Fixture.objects.filter(
            date__lte=self.date,
            home_team=self.home_team,
            home_goals__isnull=False,
            away_goals__isnull=False,
            season=self.season,
            season__current=True)\
            .order_by('-date')[:AVERAGES_OVER_LAST_N_MATCHES]
        return fixtures.aggregate(Avg('home_goals'))['home_goals__avg']

    @property
    def f_home_against_goals_avg(self):
        fixtures = Fixture.objects.filter(
            date__lte=self.date,
            home_team=self.home_team,
            home_goals__isnull=False,
            away_goals__isnull=False,
            season__league=self.season.league,
            season__current=True)\
            .order_by('-date')[:AVERAGES_OVER_LAST_N_MATCHES]
        return fixtures.aggregate(Avg('away_goals'))['away_goals__avg']

    @property
    def f_away_favor_goals_avg(self):
        fixtures = Fixture.objects.filter(
            date__lte=self.date,
            away_team=self.away_team,
            home_goals__isnull=False,
            away_goals__isnull=False,
            season__league=self.season.league,)\
            .order_by('-date')[:AVERAGES_OVER_LAST_N_MATCHES]
        return fixtures.aggregate(Avg('away_goals'))['away_goals__avg']

    @property
    def f_away_against_goals_avg(self):
        fixtures = Fixture.objects.filter(
            date__lte=self.date,
            away_team=self.away_team,
            home_goals__isnull=False,
            away_goals__isnull=False,
            season__league=self.season.league,)\
            .order_by('-date')[:AVERAGES_OVER_LAST_N_MATCHES]
        return fixtures.aggregate(Avg('home_goals'))['home_goals__avg']

    @property
    def f_home_league_goals_avg(self):
        fixtures = Fixture.objects.filter(
            date__lte=self.date,
            home_goals__isnull=False,
            away_goals__isnull=False,
            season__league=self.season.league,)\
            .order_by('-date')
        return fixtures.aggregate(Avg('home_goals'))['home_goals__avg']

    @property
    def f_away_league_goals_avg(self):
        fixtures = Fixture.objects.filter(
            date__lte=self.date,
            home_goals__isnull=False,
            away_goals__isnull=False,
            season__league=self.season.league,)\
            .order_by('-date')
        return fixtures.aggregate(Avg('away_goals'))['away_goals__avg']

    @property
    def f_home_n(self):
        fixtures = Fixture.objects.filter(
            date__lte=self.date,
            home_team=self.home_team,
            home_goals__isnull=False,
            away_goals__isnull=False,
            season=self.season,
            season__current=True)\
            [:AVERAGES_OVER_LAST_N_MATCHES]
        return fixtures.aggregate(Count('id'))['id__count']

    @property
    def f_away_n(self):
        fixtures = Fixture.objects.filter(
            date__lte=self.date,
            away_team=self.away_team,
            home_goals__isnull=False,
            away_goals__isnull=False,
            season=self.season,
            season__current=True)\
            [:AVERAGES_OVER_LAST_N_MATCHES]
        return fixtures.aggregate(Count('id'))['id__count']

    @property
    def f_league_n(self):
        fixtures = Fixture.objects.filter(
            date__lte=self.date,
            home_goals__isnull=False,
            away_goals__isnull=False,
            season=self.season,
            season__current=True)
        return fixtures.aggregate(Count('id'))['id__count']



class Odds(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    bookmaker = models.ForeignKey(BookMaker, on_delete=models.CASCADE)
    bet = models.ForeignKey(Bet, on_delete=models.CASCADE)
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE, null=True)

    def __str__(self):
        home_team_name = self.fixture.home_team.name if self.fixture.home_team else 'N/A'
        away_team_name = self.fixture.away_team.name if self.fixture.away_team else 'N/A'
        return f'{self.bet.name} ({self.bookmaker}): {home_team_name} - {away_team_name}'


class OddValues(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    odd = models.ForeignKey(Odds, on_delete=models.CASCADE)
    key = models.CharField(max_length=32)
    prob_name = models.CharField(max_length=32, blank=True)
    value = models.FloatField()

    def __str__(self):
        return f'<Odd: id={self.odd.pk}> {self.odd.bet.name}: {self.key}'


class UserBets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now=True)
    amount = models.FloatField(null=True)


class UserBetItems(models.Model):
    userbet = models.ForeignKey(UserBets, on_delete=models.CASCADE)
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    odd_value = models.ForeignKey(OddValues, on_delete=models.CASCADE)
    value = models.FloatField(null=True)
    fixed_value = models.BooleanField(default=False)

@receiver(post_save, sender=UserBetItems, dispatch_uid="update_bet")
def update_bet(sender, instance, **kwargs):
    if not instance.fixed_value:
        return

    items = UserBetItems.objects.filter(userbet=instance.userbet, fixed_value=False).exclude(pk=instance.pk)
    if items.count() == 0:
        return

    rate = (instance.userbet.amount - UserBetItems.objects.filter(userbet=instance.userbet, fixed_value=True).aggregate(sum=Sum('value'))['sum']) / items.aggregate(sum=Sum('value'))['sum']
    if rate < 0:
        raise ValueError

    for item in items:
        UserBetItems.objects.filter(pk=item.pk).update(value = rate * item.value)


class Stats(models.Model):
    fixture = models.OneToOneField(Fixture, on_delete=models.CASCADE, primary_key=True)
    home_shots_on_goal = models.IntegerField(null=True)
    away_shots_on_goal = models.IntegerField(null=True)
    home_shots_off_goal = models.IntegerField(null=True)
    away_shots_off_goal = models.IntegerField(null=True)
    home_total_shots = models.IntegerField(null=True)
    away_total_shots = models.IntegerField(null=True)
    home_blocked_shots = models.IntegerField(null=True)
    away_blocked_shots = models.IntegerField(null=True)
    home_shots_inside_box = models.IntegerField(null=True)
    away_shots_inside_box = models.IntegerField(null=True)
    home_shots_outside_box = models.IntegerField(null=True)
    away_shots_outside_box = models.IntegerField(null=True)
    home_fouls = models.IntegerField(null=True)
    away_fouls = models.IntegerField(null=True)
    home_corners = models.IntegerField(null=True)
    away_corners = models.IntegerField(null=True)
    home_offsides = models.IntegerField(null=True)
    away_offsides = models.IntegerField(null=True)
    home_ball_possession = models.IntegerField(null=True)
    away_ball_possession = models.IntegerField(null=True)
    home_yellow_cards = models.IntegerField(null=True)
    away_yellow_cards = models.IntegerField(null=True)
    home_red_cards = models.IntegerField(null=True)
    away_red_cards = models.IntegerField(null=True)
    home_goalkeeper_saves = models.IntegerField(null=True)
    away_goalkeeper_saves = models.IntegerField(null=True)
    home_total_passes = models.IntegerField(null=True)
    away_total_passes = models.IntegerField(null=True)
    home_passes_accurate = models.IntegerField(null=True)
    away_passes_accurate = models.IntegerField(null=True)

    def __str__(self):
        return f'Stats for Fixture {self.fixture}'

    # Shots on Goal Averages
    @property
    def f_home_favor_shots_on_goal_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_shots_on_goal__isnull=False,
            away_shots_on_goal__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_shots_on_goal'))['home_shots_on_goal__avg']

    @property
    def f_home_against_shots_on_goal_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_shots_on_goal__isnull=False,
            away_shots_on_goal__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_shots_on_goal'))['away_shots_on_goal__avg']

    @property
    def f_away_favor_shots_on_goal_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_shots_on_goal__isnull=False,
            away_shots_on_goal__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_shots_on_goal'))['home_shots_on_goal__avg']

    @property
    def f_away_against_shots_on_goal_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_shots_on_goal__isnull=False,
            away_shots_on_goal__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_shots_on_goal'))['away_shots_on_goal__avg']

    # Shots off Goal Averages
    @property
    def f_home_favor_shots_off_goal_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_shots_off_goal__isnull=False,
            away_shots_off_goal__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_shots_off_goal'))['home_shots_off_goal__avg']

    @property
    def f_home_against_shots_off_goal_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_shots_off_goal__isnull=False,
            away_shots_off_goal__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_shots_off_goal'))['away_shots_off_goal__avg']

    @property
    def f_away_favor_shots_off_goal_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_shots_off_goal__isnull=False,
            away_shots_off_goal__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_shots_off_goal'))['home_shots_off_goal__avg']

    @property
    def f_away_against_shots_off_goal_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_shots_off_goal__isnull=False,
            away_shots_off_goal__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_shots_off_goal'))['away_shots_off_goal__avg']

    # Total shots Averages
    @property
    def f_home_favor_total_shots_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_total_shots__isnull=False,
            away_total_shots__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_total_shots'))['home_total_shots__avg']

    @property
    def f_home_against_total_shots_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_total_shots__isnull=False,
            away_total_shots__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_total_shots'))['away_shots_total_shots__avg']

    @property
    def f_away_favor_total_shots_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_total_shots__isnull=False,
            away_total_shots__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_total_shots'))['home_total_shots__avg']

    @property
    def f_away_against_total_shots_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_total_shots__isnull=False,
            away_total_shots__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_total_shots'))['away_total_shots__avg']

    # Blocked shots Averages
    @property
    def f_home_favor_blocked_shots_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_blocked_shots__isnull=False,
            away_blocked_shots__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_blocked_shots'))['home_blocked_shots__avg']

    @property
    def f_home_against_blocked_shots_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_blocked_shots__isnull=False,
            away_blocked_shots__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_blocked_shots'))['away_blocked_total_shots__avg']

    @property
    def f_away_favor_blocked_shots_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_blocked_shots__isnull=False,
            away_blocked_shots__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_blocked_shots'))['home_blocked_shots__avg']

    @property
    def f_away_against_blocked_shots_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_blocked_shots__isnull=False,
            away_blocked_shots__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_blocked_shots'))['away_blocked_shots__avg']

    # Shots inside box Averages
    @property
    def f_home_favor_shots_inside_box_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_shots_inside_box__isnull=False,
            away_shots_inside_box__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_shots_inside_box'))['home_shots_inside_box__avg']

    @property
    def f_home_against_shots_inside_box_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_shots_inside_box__isnull=False,
            away_shots_inside_box__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_shots_inside_box'))['away_shots_inside_box__avg']

    @property
    def f_away_favor_shots_inside_box_avg(self):    
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_shots_inside_box__isnull=False,
            away_shots_inside_box__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_shots_inside_box'))['home_shots_inside_box__avg']

    @property
    def f_away_against_shots_inside_box_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_shots_inside_box__isnull=False,
            away_shots_inside_box__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_shots_inside_box'))['away_shots_inside_box__avg']

    # Shots outside box Averages
    @property
    def f_home_favor_shots_outside_box_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_shots_outside_box__isnull=False,
            away_shots_outside_box__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_shots_outside_box'))['home_shots_outside_box__avg']

    @property
    def f_home_against_shots_outside_box_avg(self):   
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_shots_outside_box__isnull=False,
            away_shots_outside_box__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_shots_outside_box'))['away_shots_outside_box__avg']

    @property
    def f_away_favor_shots_outside_box_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_shots_outside_box__isnull=False,
            away_shots_outside_box__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_shots_outside_box'))['home_shots_outside_box__avg'] 

    @property
    def f_away_against_shots_outside_box_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_shots_outside_box__isnull=False,
            away_shots_outside_box__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_shots_outside_box'))['away_shots_outside_box__avg']

    # Fouls Averages
    @property
    def f_home_favor_fouls_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_fouls__isnull=False,
            away_fouls__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_fouls'))['home_fouls__avg']

    @property
    def f_home_against_fouls_avg(self):  
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.home_team,
            home_fouls__isnull=False,
            away_fouls__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_fouls'))['away_fouls__avg']

    @property
    def f_away_favor_fouls_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_fouls__isnull=False,
            away_fouls__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('home_fouls'))['home_fouls__avg']

    @property
    def f_away_against_fouls_avg(self):
        fixtures = Stats.objects.filter(
            fixture__date__lte=self.fixture.date,
            fixture__home_team=self.fixture.away_team,
            home_fouls__isnull=False,
            away_fouls__isnull=False,
            fixture__season=self.fixture.season,
            fixture__season__current=True)\
            .order_by('-fixture__date')[:10]
        return fixtures.aggregate(Avg('away_fouls'))['away_fouls__avg']

    