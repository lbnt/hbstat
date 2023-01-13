from django.core.management.base import BaseCommand, CommandError

from django.db.models import Sum
from django.db.models import Count
from django.db.models import Avg

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
    
    for myplayer in DPlayer.objects.all():
        print("Updating player " + myplayer.id)
        
        myplayerpools=DPoolPlayer.objects.filter(player=myplayer.id)
        myplayerstatscount=DPoolPlayerStat.objects.filter(player=myplayer.id).count()
        myplayerstats=DPoolPlayerStat.objects.filter(player=myplayer.id).aggregate(Sum('goal'), Avg('goal'), Avg('saves'), Sum('saves'), Sum('mins'), Sum('warn'), Sum('dis'))
        
        DPlayer.objects.filter(id=myplayer.id).update(
            game = myplayerstatscount,
            goal = myplayerstats['goal__sum'],
            avg_goal = myplayerstats['goal__avg'],
            save = myplayerstats['saves__sum'],
            avg_save = myplayerstats['saves__avg'],
            mins = myplayerstats['mins__sum'],
            warn = myplayerstats['warn__sum'],
            dis = myplayerstats['dis__sum']
        )


    

class Command(BaseCommand):
    args = ''
    help = 'Update all player stats using pool stats'

    def handle(self, *args, **options):

        # update player stats : creation or update
        update_player_stats()
