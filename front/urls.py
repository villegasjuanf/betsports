from django.urls import include, path
import front.views as views


urlpatterns = [
    path('', views.main),
    ]