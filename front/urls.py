from django.urls import include, path
import front.views as views


urlpatterns = [
    path('', views.main),
    path('next_table/', views.next_table, name="next_table"),
    path('bets_table/', views.bets_table, name="bets_table"),
    ]