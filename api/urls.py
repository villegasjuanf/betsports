from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from adrf import routers
import api.views as viewsets

router = routers.DefaultRouter()
router.register(r'country', viewsets.CountryViewSet)
router.register(r'league', viewsets.LeagueViewSet)
router.register(r'team', viewsets.TeamViewSet)
router.register(r'fixture', viewsets.FixtureViewSet)
router.register(r'odd', viewsets.OddViewSet)
router.register(r'bookmaker', viewsets.BookmakerViewSet)
router.register(r'bet', viewsets.BetViewSet)

api_urls = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'),
         name='redoc'),
]
