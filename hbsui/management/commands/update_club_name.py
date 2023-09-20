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
from difflib import SequenceMatcher


def update_club_name():

    for myclub in Club.objects.all():

        #get all teams name of this club
        mypoolteams = PoolTeam.objects.filter(club=myclub.id)

        team_names = []
        for mypoolteam in mypoolteams:
            team_names.append(mypoolteam.name)

        names_occurence = Counter(team_names)

        names = names_occurence.most_common(2)

        if len(names) == 1:
            myclub.name = names[0][0]
            myclub.save()
        elif len(names) == 2:
            # initialize SequenceMatcher object with input string
            seqMatch = SequenceMatcher(None,names[0][0],names[1][0])
            print(names[0][0])
            print(names[1][0])
        
            # find match of longest sub-string
            match = seqMatch.find_longest_match(0, len(names[0][0]), 0, len(names[1][0]))

            #TODO a ameliorer avec l'information de ration ?
            if match.size > 3 :
                myclub.name = names[0][0][match.a: match.a + match.size].strip()
                print(myclub.name)
                print('----------------')
                myclub.save()
            else:
                #bad news
                myclub.name = names[0][0]
                print('pas de correspondance')
                myclub.save()

        
    
class Command(BaseCommand):
    args = ''
    help = 'Update club names in the database'

    def handle(self, *args, **options):

        update_club_name()
        