from math import ceil
import datetime
from unidecode import unidecode
import csv
import pygal

from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.core.paginator import Paginator

from django.db.models import Sum
from django.db.models import Count
from django.db.models import Avg

from hbsui.models import Championship, Club
from hbsui.models import Competition
from hbsui.models import Phase
from hbsui.models import Pool
from hbsui.models import PoolTeam
from hbsui.models import PoolMatch
from hbsui.models import PoolDay
from hbsui.models import Player
from hbsui.models import PlayerPoolStat
from hbsui.models import PlayerMatchStat
from hbsui.models import Player
from hbsui.models import DEPARTEMENT_CHOICES
from hbsui.models import REGION_CHOICES_TO_INSEE

# Create your views here.
def welcome(request):
    mynbplayers=Player.objects.count()
    mynbpoolteams=PoolTeam.objects.count()
    mynbclubs=Club.objects.count()
    mynbpoolmatchspast=PoolMatch.objects.exclude(date__gte = datetime.datetime.now()).count()
    mynbpoolmatchsfuture=PoolMatch.objects.filter(date__gte = datetime.datetime.now()).count()
    mynbpools=Pool.objects.count()
    mynbgoals=PoolTeam.objects.aggregate(Sum('scored'))
    
    return render(request, 'hbsui/welcome.html', {'nbplayers': mynbplayers, 'nbpoolteams': mynbpoolteams, 'nbgoals' : mynbgoals, 'nbclubs': mynbclubs, 'nbpoolmatchspast': mynbpoolmatchspast,'nbpoolmatchsfuture': mynbpoolmatchsfuture, 'nbpools': mynbpools} )

def acceuil(request):
    return render(request, 'hbsui/acceuil.html')

def main(request):
    return render(request, 'hbsui/main.html')

def categories(request):
    return render(request, 'hbsui/categories.html')

def championships(request):
    mycategory = request.GET.get('categoryid','')
    if mycategory == 'DEP':
        mychampionships = Championship.objects.filter(category=mycategory).order_by('departement')
        return render(request, 'hbsui/championships.html', {'championships': mychampionships})
    elif mycategory == 'REG':
        mychampionships = Championship.objects.filter(category=mycategory).order_by('region')
        return render(request, 'hbsui/championships.html', {'championships': mychampionships})
    else:
        return HttpResponse('<div id="championships"></div>')

def competitions(request):
    mychampionshipid = request.GET.get('championshipid','')
    if mychampionshipid != '':
        mycompetitions = Competition.objects.filter(championship=mychampionshipid)
        return render(request, 'hbsui/competitions.html', {'competitions': mycompetitions})
    else:
        return HttpResponse('<div id="competitions"></div>')

def phases(request):
    mycompetitionid = request.GET.get('competitionid','')
    if mycompetitionid != '':
        myphases = Phase.objects.filter(competition=mycompetitionid)
        return render(request, 'hbsui/phases.html', {'phases': myphases})
    else:
        return HttpResponse('<div id="phases"></div>')

def pools(request):
    myphaseid = request.GET.get('phaseid','')
    if myphaseid != '':
        mypools = Pool.objects.filter(phase=myphaseid)
        return render(request, 'hbsui/pools.html', {'pools': mypools})
    else:
        return HttpResponse('<div id="pools"></div>')

def poolsdata(request):
    mypoolid = request.GET.get('poolid','')
    mypool = Pool.objects.get(pk=mypoolid)

    if request.htmx:
        base_template = "hbsui/acceuil_results_partial.html"
    else:
        base_template = "hbsui/acceuil.html"

    return render(
        request,
        'hbsui/poolsdata.html',
        {
            "base_template": base_template,
            'pool':mypool
        }
    )

def poolmatchs(request):
    mypoolid = request.GET.get('poolid','')
    mypool = Pool.objects.get(pk=mypoolid)
    poolmatchs = PoolMatch.objects.filter(pool=mypoolid)
    return render(request, 'hbsui/poolmatchs.html', {'pool':mypool, 'poolmatchs':poolmatchs,'pool_gender':mypool.phase.competition.get_gender_display(),'pool_age':mypool.phase.competition.get_age_display()})

def poolmatchfdm(request):
    myfdmcode = request.GET.get('fdm','')
    fdmurl = "https://media-ffhb-fdm.ffhandball.fr/fdm/"+ myfdmcode[0] + "/" + myfdmcode[1] + "/" + myfdmcode[2] + "/" + myfdmcode[3] + "/" + myfdmcode + ".pdf"
    response = redirect(fdmurl)
    return response

def poolmatchscsv(request):
    
    mypoolid = request.GET.get('poolid','')
    mypool = Pool.objects.get(pk=mypoolid)
    poolmatchs = PoolMatch.objects.filter(pool=mypoolid)

    csvfilename = mypool.phase.competition.championship.code + "_" + mypool.phase.competition.name + "_" + mypool.phase.name + "_" + mypool.name + "_resultats.csv";

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename='+csvfilename},
    )

    writer = csv.writer(response)
    
    if poolmatchs:
        writer.writerow(["journée", "date", "heures", "minutes", "équipe_0", "score_0", "équipe_1", "score_1", "lieu_0", "lieu_1", "lieu_2", "arbitre_0", "arbitre_1", "feuille_de_match"])

        for poolmatch in poolmatchs:
            writer.writerow([poolmatch.date_day, poolmatch.date_date, poolmatch.date_hour, poolmatch.date_minute, poolmatch.team_0_name, poolmatch.team_0_score, poolmatch.team_1_name, poolmatch.team_1_score, poolmatch.location_0, poolmatch.location_1, poolmatch.location_2, poolmatch.referee_0_name, poolmatch.referee_1_name, poolmatch.fdm])

    return response

def poolteams(request):
    mypoolid = request.GET.get('poolid','')
    poolteams = PoolTeam.objects.filter(pool=mypoolid).order_by('ranking')
    return render(request, 'hbsui/poolteams.html', {'poolid':mypoolid,'poolteams': poolteams})

def poolteamscsv(request):
    
    mypoolid = request.GET.get('poolid','')
    mypool = Pool.objects.get(pk=mypoolid)
    poolteams = PoolTeam.objects.filter(pool=mypoolid).order_by('ranking')
    
    csvfilename = mypool.phase.competition.championship.code + "_" + mypool.phase.competition.name + "_" + mypool.phase.name + "_" + mypool.name + "_classement.csv";

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename='+csvfilename},
    )

    writer = csv.writer(response)
    
    if poolteams:
        writer.writerow(["classement", "équipe", "nb_matchs_joués", "points", "victoires", "nuls", "défaites", "buts+", "buts-", "diff"])

        for poolteam in poolteams:
            writer.writerow([poolteam.ranking, poolteam.name, poolteam.games, poolteam.points, poolteam.wins, poolteam.draws, poolteam.defeats, poolteam.scored, poolteam.missed, poolteam.difference])

    return response

def poolplayers(request):
    mypoolid = request.GET.get('poolid','')
    mypoolclubs=PlayerPoolStat.objects.filter(pool=mypoolid).values('player__club__name','player__club__id').annotate(Sum('goals'))
    return render(request, 'hbsui/poolplayers.html', {'poolid':mypoolid, 'poolclubs':mypoolclubs})

def poolplayersdata(request):
    mypoolid = request.GET.get('poolid','')
    myclubid = request.GET.get('clubid','')
    myorderby = request.GET.get('orderby','-goals')
    page = request.GET.get('page',1)
    try:
        if myclubid == 'all':
            mypoolplayers=PlayerPoolStat.objects.filter(pool=mypoolid).order_by(myorderby)
        else:
            mypoolplayers=PlayerPoolStat.objects.filter(player__club__id=myclubid,pool=mypoolid).order_by(myorderby)
    except:
        mypoolplayers = None

    mynbresults=len(mypoolplayers)
    paginator = Paginator(mypoolplayers, 10)
    poolplayers = paginator.page(page)
    page_range = paginator.get_elided_page_range(number=page)

    return render(request, 'hbsui/poolplayersdata.html', {'poolplayers':poolplayers, 'nbresults':mynbresults, 'page_range':page_range})

def poolplayersdatacsv(request):
    mypoolid = request.GET.get('poolid','')
    
    mypool = Pool.objects.get(pk=mypoolid)
    
    mypoolplayers=PlayerPoolStat.objects.filter(pool=mypoolid)
    
    csvfilename = mypool.phase.competition.championship.code + "_" + mypool.phase.competition.name + "_" + mypool.phase.name + "_" + mypool.name + "_joueurs.csv";

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename='+csvfilename},
    )

    writer = csv.writer(response)
    
    if mypoolplayers:
        writer.writerow(["club", "nom", "prénom", "nb_matchs_joués", "buts", "arrêts", "moyenne_buts", "moyenne_arrêts"])

        for mypoolplayer in mypoolplayers:
            writer.writerow([mypoolplayer.player.club.name, mypoolplayer.player.last_name, mypoolplayer.player.first_name, mypoolplayer.match_played, mypoolplayer.goals, mypoolplayer.saves, mypoolplayer.avg_goals, mypoolplayer.avg_saves])

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
        filterdict['first_name__icontains'] = unidecode(myfirst_name.strip())
    if len(mylast_name) > 0:
        filterdict['last_name__icontains'] = unidecode(mylast_name.strip())
    if len(myname) > 0:
        filterdict['club__name__icontains'] = unidecode(myname.strip())
    if mygender == 'M' or mygender == 'F' :
        filterdict['gender'] = mygender
    
    myplayers=Player.objects.filter(**filterdict)
    mynbresults=len(myplayers)
    paginator = Paginator(myplayers, 10)
    players = paginator.page(page)
    page_range = paginator.get_elided_page_range(number=page)
    
    
    return render(request, 'hbsui/playerssearchresults.html', {'players':players, 'nbresults':mynbresults, 'page_range':page_range})

def playerdata(request):
    myplayerid = request.GET.get('id','')
    
    myplayer=Player.objects.get(id=myplayerid)
    myplayerpools=PlayerPoolStat.objects.filter(player=myplayerid)
 
    if request.htmx:
        base_template = "hbsui/acceuil_results_partial.html"
    else:
        base_template = "hbsui/acceuil.html"

    return render(
        request,
        'hbsui/playerdata.html',
        {
            "base_template": base_template,
            'player':myplayer,
            'playerpools':myplayerpools
        }
    )

def playerdatastat(request):
    mypoolid = request.GET.get('poolid','')
    myplayerid = request.GET.get('playerid','')
    
    mypool = Pool.objects.get(id=mypoolid)
    myplayermatchstats=PlayerMatchStat.objects.filter(player=myplayerid,pool=mypoolid)  
    return render(request, 'hbsui/playerdatastat.html', {'pool':mypool,'playermatchstats':myplayermatchstats})

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
    
    myclubs=Club.objects.filter(**filterdict).order_by('name')
    nb_clubs=len(myclubs)
    paginator = Paginator(myclubs, 10)
    clubs = paginator.page(page)
    page_range = paginator.get_elided_page_range(number=page)
    
    return render(request, 'hbsui/clubssearchresults.html', {'clubs':clubs, 'nb_clubs':nb_clubs, 'page_range':page_range})

def clubdata(request):
    myclubid = request.GET.get('id','')
    
    myclub=Club.objects.get(id=myclubid)

    if request.htmx:
        base_template = "hbsui/acceuil_results_partial.html"
    else:
        base_template = "hbsui/acceuil.html"

    return render(
        request,
        'hbsui/clubdata.html',
        {
            "base_template": base_template,
            'club':myclub
        }
    )

def clubdataplayers(request):
    myclubid = request.GET.get('id','')
    page = request.GET.get('page',1)
    
    myclub=Club.objects.get(id=myclubid)
    myplayers=Player.objects.filter(club=myclubid).order_by('last_name')

    mynbresults=len(myplayers)

    paginator = Paginator(myplayers, 10)
    players = paginator.page(page)
    page_range = paginator.get_elided_page_range(number=page)
    
    return render(request, 'hbsui/clubdataplayers.html', {'players':players,'nbresults':mynbresults, 'page_range':page_range})

def clubdatapools(request):
    myclubid = request.GET.get('id','')
    page = request.GET.get('page',1)
    
    myclubpools=PoolTeam.objects.filter(club=myclubid).values('name', 'pool__phase__name','pool__phase__competition__name','pool__name','pool__id').annotate(dcount=Count('pool__id')).order_by('pool__phase__competition__name','pool__phase__name')

    mynbresults=len(myclubpools)

    paginator = Paginator(myclubpools, 10)
    clubpools = paginator.page(page)
    page_range = paginator.get_elided_page_range(number=page)

    return render(request, 'hbsui/clubdatapools.html', {'clubpools':clubpools,'nbresults':mynbresults, 'page_range':page_range})

def top(request):
    mytopgoalscorers = Player.objects.order_by('-goals')[:10]
    return render(request, 'hbsui/top.html', {'topgoalscorers':mytopgoalscorers})

def favorites(request):
    return render(request, 'hbsui/favorites.html')

def maps(request):
    return render(request, 'hbsui/maps.html')


def generatemaps(request):

    mytype = request.GET.get('type','T')
    mylevel = request.GET.get('level','D')

    myplayerdata = {}
    myclubdata = {}
    filterdict = {}

    if mytype == 'M' or mytype == 'F' or mytype == 'T':
        if mytype == 'M':
            filterdict['gender__exact'] = 'M'
            data_title = 'Nombre de joueurs (M)'
        elif mytype == 'F':
            filterdict['gender__exact'] = 'F'
            data_title = 'Nombre de joueuses (F)'
        elif mytype == 'T':
            data_title = 'Nombre de joueurs (M+F)'

        if mylevel == 'D':
            for dep_code, dep_name in DEPARTEMENT_CHOICES:
                filterdict['club__departement__exact'] = dep_code
                myplayerdata[dep_code] = Player.objects.filter(**filterdict).count()
            
            fr_chart = pygal.maps.fr.Departments(show_legend=False, human_readable=True, fill=True)
            fr_chart.add(data_title, myplayerdata)
            
        elif mylevel == 'R':
            for reg_code, reg_insee in REGION_CHOICES_TO_INSEE:
                filterdict['club__region__exact'] = reg_code
                myplayerdata[reg_insee] = Player.objects.filter(**filterdict).count()
            
            fr_chart = pygal.maps.fr.Regions(show_legend=False, human_readable=True, fill=True)
            fr_chart.add(data_title, myplayerdata)


    elif mytype == 'C':
        data_title = 'Nombre de clubs'
        
        if mylevel == 'D':
            for dep_code, dep_name in DEPARTEMENT_CHOICES:
                filterdict['departement'] = dep_code
                myclubdata[dep_code] = Club.objects.filter(**filterdict).count()
            
            fr_chart = pygal.maps.fr.Departments(show_legend=False, human_readable=True, fill=True)
            fr_chart.add(data_title, myclubdata)
            
        elif mylevel == 'R':
            for reg_code, reg_insee in REGION_CHOICES_TO_INSEE:
                filterdict['region'] = reg_code
                myclubdata[reg_insee] = Club.objects.filter(**filterdict).count()
            
            fr_chart = pygal.maps.fr.Regions(show_legend=False, human_readable=True, fill=True)
            fr_chart.add(data_title, myclubdata)    

    return render(request, 'hbsui/mapdata.html', {'chart' : fr_chart.render_data_uri(), 'title' : data_title})