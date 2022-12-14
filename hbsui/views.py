from math import ceil
import datetime
from unidecode import unidecode
import csv

from django.http import HttpResponse
from django.shortcuts import render

from django.core.paginator import Paginator

from django.db.models import Sum
from django.db.models import Count

from hbsui.models import DChampionship, DClub
from hbsui.models import DCompetition
from hbsui.models import DPool
from hbsui.models import DPoolTeam
from hbsui.models import DPoolEvent
from hbsui.models import DPoolDate
from hbsui.models import DPoolPlayer
from hbsui.models import DPoolPlayerStat
from hbsui.models import DPlayer

# Create your views here.
def welcome(request):
    mynbplayers=DPlayer.objects.count()
    mynbpoolteams=DPoolTeam.objects.count()
    mynbclubs=DClub.objects.count()
    mynbpooleventspast=DPoolEvent.objects.exclude(date_date__gte = datetime.datetime.now()).count()
    mynbpooleventsfuture=DPoolEvent.objects.filter(date_date__gte = datetime.datetime.now()).count()
    print(DPoolEvent.objects.count())
    mynbpools=DPool.objects.count()
    mynbgoals=DPoolTeam.objects.aggregate(Sum('scored'))
    
    return render(request, 'hbsui/welcome.html', {'nbplayers': mynbplayers, 'nbpoolteams': mynbpoolteams, 'nbgoals' : mynbgoals, 'nbclubs': mynbclubs, 'nbpooleventspast': mynbpooleventspast,'nbpooleventsfuture': mynbpooleventsfuture, 'nbpools': mynbpools} )

def acceuil(request):
    return render(request, 'hbsui/acceuil.html')

def main(request):
    return render(request, 'hbsui/main.html')

def categories(request):
    return render(request, 'hbsui/categories.html')

def championships(request):
    mycategory = request.GET.get('categoryid','D')
    mychampionships = DChampionship.objects.filter(category=mycategory).order_by('code')
    return render(request, 'hbsui/championships.html', {'championships': mychampionships})

def competitions(request):
    mychampionshipid = request.GET.get('championshipid','')
    mycompetitions = DCompetition.objects.filter(championship=mychampionshipid)
    return render(request, 'hbsui/competitions.html', {'competitions': mycompetitions})

def pools(request):
    mycompetitionid = request.GET.get('competitionid','')
    mypools = DPool.objects.filter(competition=mycompetitionid)
    return render(request, 'hbsui/pools.html', {'pools': mypools})

def poolsdata(request):
    return render(request, 'hbsui/poolsdata.html')

def poolevents(request):
    mypoolid = request.GET.get('poolid','')
    mypool = DPool.objects.get(pk=mypoolid)
    poolevents = DPoolEvent.objects.filter(pool=mypoolid)
    return render(request, 'hbsui/poolevents.html', {'poolid':mypoolid,'poolevents':poolevents,'pool_gender':mypool.get_gender_display(),'pool_age':mypool.get_age_display()})

def pooleventscsv(request):
    
    mypoolid = request.GET.get('poolid','')
    mypool = DPool.objects.get(pk=mypoolid)
    poolevents = DPoolEvent.objects.filter(pool=mypoolid)

    csvfilename = mypool.competition.championship.code + "_" + mypool.competition.name + "_" + mypool.phase_name + "_" + mypool.name + "_resultats.csv";

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename='+csvfilename},
    )

    writer = csv.writer(response)
    
    if poolevents:
        writer.writerow(["journ??e", "date", "heures", "minutes", "??quipe_0", "score_0", "??quipe_1", "score_1", "lieu_0", "lieu_1", "lieu_2", "arbitre_0", "arbitre_1", "feuille_de_match"])

        for poolevent in poolevents:
            writer.writerow([poolevent.date_day, poolevent.date_date, poolevent.date_hour, poolevent.date_minute, poolevent.team_0_name, poolevent.team_0_score, poolevent.team_1_name, poolevent.team_1_score, poolevent.location_0, poolevent.location_1, poolevent.location_2, poolevent.referee_0_name, poolevent.referee_1_name, poolevent.fdm])

    return response

def poolteams(request):
    mypoolid = request.GET.get('poolid','')
    poolteams = DPoolTeam.objects.filter(pool=mypoolid).order_by('position')
    return render(request, 'hbsui/poolteams.html', {'poolid':mypoolid,'poolteams': poolteams})

def poolteamscsv(request):
    
    mypoolid = request.GET.get('poolid','')
    mypool = DPool.objects.get(pk=mypoolid)
    poolteams = DPoolTeam.objects.filter(pool=mypoolid).order_by('position')
    
    csvfilename = mypool.competition.championship.code + "_" + mypool.competition.name + "_" + mypool.phase_name + "_" + mypool.name + "_classement.csv";

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename='+csvfilename},
    )

    writer = csv.writer(response)
    
    if poolteams:
        writer.writerow(["classement", "??quipe", "nb_matchs_jou??s", "points", "victoires", "nuls", "d??faites", "buts+", "buts-", "diff"])

        for poolteam in poolteams:
            writer.writerow([poolteam.position, poolteam.team_name, poolteam.games, poolteam.points, poolteam.wins, poolteam.draws, poolteam.defeats, poolteam.scored, poolteam.missed, poolteam.difference])

    return response

def poolplayers(request):
    mypoolid = request.GET.get('poolid','')
    mypoolclubs=DPoolPlayer.objects.filter(pool=mypoolid).values('player__club__name','player__club__id').annotate(Sum('goal'))
    return render(request, 'hbsui/poolplayers.html', {'poolid':mypoolid, 'poolclubs':mypoolclubs})

def poolplayersdata(request):
    mypoolid = request.GET.get('poolid','')
    myclubid = request.GET.get('clubid','')
    myorderby = request.GET.get('orderby','-goal')
    page = request.GET.get('page',1)
    try:
        if myclubid == 'all':
            mypoolplayers=DPoolPlayer.objects.filter(pool=mypoolid).order_by(myorderby)
        else:
            mypoolplayers=DPoolPlayer.objects.filter(player__club__id=myclubid,pool=mypoolid).order_by(myorderby)
    except:
        mypoolplayers = None

    mynbresults=len(mypoolplayers)
    paginator = Paginator(mypoolplayers, 10)
    poolplayers = paginator.page(page)
    page_range = paginator.get_elided_page_range(number=page)

    return render(request, 'hbsui/poolplayersdata.html', {'poolplayers':poolplayers, 'nbresults':mynbresults, 'page_range':page_range})

def poolplayersdatacsv(request):
    mypoolid = request.GET.get('poolid','')
    
    mypool = DPool.objects.get(pk=mypoolid)
    
    mypoolplayers=DPoolPlayer.objects.filter(pool=mypoolid)
    
    csvfilename = mypool.competition.championship.code + "_" + mypool.competition.name + "_" + mypool.phase_name + "_" + mypool.name + "_joueurs.csv";

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename='+csvfilename},
    )

    writer = csv.writer(response)
    
    if mypoolplayers:
        writer.writerow(["club", "nom", "pr??nom", "nb_matchs_jou??s", "buts", "arr??ts", "moyenne_buts", "moyenne_arr??ts"])

        for mypoolplayer in mypoolplayers:
            writer.writerow([mypoolplayer.player.club.name, mypoolplayer.player.last_name, mypoolplayer.player.first_name, mypoolplayer.match_played, mypoolplayer.goal, mypoolplayer.saves, mypoolplayer.avg, mypoolplayer.avg_stop])

    return response

def clubs(request):
    return render(request, 'hbsui/clubs.html')

def players(request):
    return render(request, 'hbsui/players.html')

def searchplayers(request):
    myfirst_name = request.GET.get('first_name','')
    mylast_name = request.GET.get('last_name','')
    myname = request.GET.get('name','')
    mygender = request.GET.get('gender','')
    page = request.GET.get('page',1)
    
    filterdict = {}

    if len(myfirst_name) > 0:
        filterdict['first_name__icontains'] = unidecode(myfirst_name)
    if len(mylast_name) > 0:
        filterdict['last_name__icontains'] = unidecode(mylast_name)
    if len(myname) > 0:
        filterdict['club__name__icontains'] = unidecode(myname)
    if mygender == 'M' or mygender == 'F' :
        filterdict['gender'] = mygender
    
    myplayers=DPlayer.objects.filter(**filterdict)
    mynbresults=len(myplayers)
    paginator = Paginator(myplayers, 10)
    players = paginator.page(page)
    page_range = paginator.get_elided_page_range(number=page)
    
    
    return render(request, 'hbsui/playerssearchresults.html', {'players':players, 'nbresults':mynbresults, 'page_range':page_range})

def playerdata(request):
    myplayerid = request.GET.get('id','')
    
    myplayer=DPlayer.objects.get(id=myplayerid)
    myplayerpools=DPoolPlayer.objects.filter(player=myplayerid)
    
    return render(request, 'hbsui/playerdata.html', {'player':myplayer,'playerpools':myplayerpools})

def playerdatastat(request):
    mypoolid = request.GET.get('id','')
    myplayerid = request.GET.get('id','')
    
    mypool = DPool.objects.get(id=mypoolid)
    myplayerpoolstats=DPoolPlayerStat.objects.filter(player=myplayerid,pool=mypoolid)
    return render(request, 'hbsui/playerdatastat.html', {'pool':mypool,'playerpoolstats':myplayerpoolstats})

def emptymodal(request):
    return HttpResponse('<div class=\"modal\"></div>')

def searchclubs(request):
    myname = request.GET.get('name','')
    mydepartement = request.GET.get('departement','')
    page = request.GET.get('page',1)
    
    filterdict = {}

    if len(myname) > 0:
        filterdict['name__icontains'] = unidecode(myname)
    
    if len(mydepartement) >= 1:
        filterdict['departement__exact'] = mydepartement
    
    myclubs=DClub.objects.filter(**filterdict).order_by('name')
    nb_clubs=len(myclubs)
    paginator = Paginator(myclubs, 10)
    clubs = paginator.page(page)
    page_range = paginator.get_elided_page_range(number=page)
    
    return render(request, 'hbsui/clubssearchresults.html', {'clubs':clubs, 'nb_clubs':nb_clubs, 'page_range':page_range})

def clubdata(request):
    myclubid = request.GET.get('id','')
    
    myclub=DClub.objects.get(id=myclubid)
    
    return render(request, 'hbsui/clubdata.html', {'club':myclub})

def clubdataplayers(request):
    myclubid = request.GET.get('id','')
    page = request.GET.get('page',1)
    
    myclub=DClub.objects.get(id=myclubid)
    myplayers=DPlayer.objects.filter(club=myclubid).order_by('last_name')

    mynbresults=len(myplayers)

    paginator = Paginator(myplayers, 10)
    players = paginator.page(page)
    page_range = paginator.get_elided_page_range(number=page)
    
    return render(request, 'hbsui/clubdataplayers.html', {'players':players,'nbresults':mynbresults, 'page_range':page_range})

def clubdatapools(request):
    myclubid = request.GET.get('id','')
    page = request.GET.get('page',1)
    
    myclubpools=DClub.objects.filter(id=myclubid).values('dplayer__dpoolplayer__pool__name', 'dplayer__dpoolplayer__pool__phase_name','dplayer__dpoolplayer__pool__competition__name').annotate(dcount=Count('dplayer__dpoolplayer__pool__id')).order_by('dplayer__dpoolplayer__pool__competition__name','dplayer__dpoolplayer__pool__phase_name')

    mynbresults=len(myclubpools)

    paginator = Paginator(myclubpools, 10)
    clubpools = paginator.page(page)
    page_range = paginator.get_elided_page_range(number=page)

    return render(request, 'hbsui/clubdatapools.html', {'clubpools':clubpools,'nbresults':mynbresults, 'page_range':page_range})
