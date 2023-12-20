from django.core.management.base import BaseCommand, CommandError

from hbsui.models import Championship
from hbsui.models import Club
from hbsui.models import Competition
from hbsui.models import Phase
from hbsui.models import Pool
from hbsui.models import PoolTeam
from hbsui.models import PoolDay
from hbsui.models import PoolMatch
from hbsui.models import PlayerMatchStat
from hbsui.models import PlayerPoolStat
from hbsui.models import Player
from hbsui.models import Gym

from collections import Counter
import re


def update_club_name():

    for myclub in Club.objects.all():

        #get all teams name of this club
        mypoolteams = PoolTeam.objects.filter(club=myclub.id)

        team_names = []
        for mypoolteam in mypoolteams:
            #remove team number
            clean_pool_teamname = re.sub('( .| \d)$', '', mypoolteam.name)
            team_names.append(clean_pool_teamname)

        names_occurence = Counter(team_names)

        #get most common team name as club name
        names = names_occurence.most_common(2)

        #some club don't have a team!
        if len(names) >= 1:
            myclub.name = names[0][0]
            myclub.save()

        
    
class Command(BaseCommand):
    args = ''
    help = 'Update club names in the database'

    def handle(self, *args, **options):

        update_club_name()
        