from django.core.management.base import BaseCommand, CommandError

from hbsui.models import DChampionship, DClub
from hbsui.models import DCompetition
from hbsui.models import DPool
from hbsui.models import DPoolTeam
from hbsui.models import DPoolDate
from hbsui.models import DPoolEvent
from hbsui.models import DPoolPlayer
from hbsui.models import DPoolPlayerStat
from hbsui.models import DPlayer

def update_player_stats():
    myplayer=DPlayer.objects.get(id=myplayerid)
    myplayerpools=DPoolPlayer.objects.filter(player=myplayerid)
    myplayerstatscount=DPoolPlayerStat.objects.filter(player=myplayerid).count()
    myplayerstats=DPoolPlayerStat.objects.filter(player=myplayerid).aggregate(Sum('goal'), Avg('goal'), Avg('saves'), Sum('saves'), Sum('mins'), Sum('warn'), Sum('dis'))
    

class Command(BaseCommand):
    args = ''
    help = 'Update -Championnats départementaux- database'

    def handle(self, *args, **options):

        # update player stats : creation or update
        update_player_stats()
