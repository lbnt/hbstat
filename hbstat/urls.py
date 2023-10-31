"""hbstat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hbsui import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('welcome/', views.welcome),
    path('acceuil/', views.acceuil),
    path('', views.acceuil),
    path('main/', views.main),
    path('categories/', views.categories),
    path('championships/', views.championships),
    path('competitions/', views.competitions),
    path('phases/', views.phases),
    path('pools/', views.pools),
    path('poolsdata/', views.poolsdata),
    path('poolplayers/', views.poolplayers),
    path('poolmatchs/', views.poolmatchs),
    path('poolmatchfdm/', views.poolmatchfdm),
    path('poolmatchscsv/', views.poolmatchscsv),
    path('poolteams/', views.poolteams),
    path('poolteamscsv/', views.poolteamscsv),
    path('poolplayersdata/', views.poolplayersdata),
    path('poolplayersdatacsv/', views.poolplayersdatacsv),
    path('clubs/', views.clubs),
    path('players/', views.players),
    path('searchplayers/', views.searchplayers),
    path('playerdata/', views.playerdata),
    path('playerdatastat/', views.playerdatastat),
    path('emptymodal/', views.emptymodal),
    path('searchclubs/', views.searchclubs),
    path('clubdata/', views.clubdata),
    path('clubdataplayers/', views.clubdataplayers),
    path('clubdatapools/', views.clubdatapools),
    path('top/', views.top),
    path('favorites/', views.favorites),
]
