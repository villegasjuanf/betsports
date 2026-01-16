from django.db.models import Sum
import pytest
from extractor.models import UserBets, UserBetItems

@pytest.fixture
def userbet(admin):
    userbet = UserBets(user=admin, amount=100)
    userbet.save()
    return UserBets.objects.get(user=admin)

@pytest.fixture
def items(userbet, bet, fixture, odds):
    bet1 = UserBetItems(id=1, userbet=userbet, fixture=fixture, odd_value=odds, value=30., fixed_value=True)
    bet2 = UserBetItems(id=2, userbet=userbet, fixture=fixture, odd_value=odds, value=30., fixed_value=False)
    bet3 = UserBetItems(id=3, userbet=userbet, fixture=fixture, odd_value=odds, value=40., fixed_value=False)
    bet1.save()
    bet2.save()
    bet3.save()
    return UserBetItems.objects.filter(userbet=userbet)

@pytest.fixture
def updated_items(items, userbet, fixture, odds):
    bet = UserBetItems(id=4, userbet=userbet, fixture=fixture, odd_value=odds, value=50, fixed_value=True)
    bet.save()
    return UserBetItems.objects.filter(userbet=userbet)


class TestUserBets:

    def test_bets(self, items, userbet):
        assert userbet.amount == 100
        assert items.aggregate(sum=Sum('value'))['sum'] == 100

    def test_update_bets(self, updated_items):
        assert updated_items.filter(id=1).first().value == 30
        assert updated_items.filter(id=4).first().value == 50
        assert updated_items.filter(id=2).first().value == pytest.approx(8.57, abs=0.1)
        assert updated_items.filter(id=3).first().value == pytest.approx(11.42, abs=0.1)