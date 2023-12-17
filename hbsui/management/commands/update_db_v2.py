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


from django.db.models import Sum
from django.db.models import Count
from django.db.models import Avg

import requests
import json
import hashlib
from bs4 import BeautifulSoup
import base64
from datetime import datetime, date, timezone
import io
import fitz
import re
import os

from collections import Counter
from difflib import SequenceMatcher

from django.utils.timezone import get_current_timezone


#TODO maj periodique des noms de club
#TODO calcul des stats joueurs totales et par poule


base_url = "https://www.ffhandball.fr/wp-json/competitions/v1/computeBlockAttributes/"

def update_player_pool_stats(player_obj, pool_obj):
    
    #update pool stats

    myplayermatchstatscount = PlayerMatchStat.objects.filter(player=player_obj.id, pool=pool_obj.id).count()
    
    myplayerpoolstats = PlayerMatchStat.objects.filter(player=player_obj.id, pool=pool_obj.id).aggregate(Sum('goals'), Sum('penaltythrows'), Sum('shots'), Sum('saves'), Sum('mins'), Sum('warn'), Sum('dis'), Avg('goals'), Avg('saves'))
    
    id = player_obj.id + "_" + pool_obj.id

    PlayerPoolStat.objects.update_or_create(
        id = id,
        defaults = {
            'player' : player_obj,
            'pool' : pool_obj,
            'match_played'  : myplayermatchstatscount,
            'goals'  : myplayerpoolstats['goals__sum'],
            'penaltythrows'  : myplayerpoolstats['penaltythrows__sum'],
            'shots'  : myplayerpoolstats['shots__sum'],
            'saves'  : myplayerpoolstats['saves__sum'],
            'mins'  : myplayerpoolstats['mins__sum'],
            'warn'  : myplayerpoolstats['warn__sum'],
            'dis'  : myplayerpoolstats['dis__sum'],
            'avg_goals'  : myplayerpoolstats['goals__avg'],
            'avg_saves'  : myplayerpoolstats['saves__avg']
        }
    )

def update_player_stats(player_obj):

    #update global stats

    myplayermatchstatscount = PlayerMatchStat.objects.filter(player=player_obj.id).count()
    
    myplayerstats = PlayerMatchStat.objects.filter(player=player_obj.id).aggregate(Sum('goals'), Sum('penaltythrows'), Sum('shots'), Sum('saves'), Sum('mins'), Sum('warn'), Sum('dis'), Avg('goals'), Avg('saves'))

    Player.objects.filter(id=player_obj.id).update(
        match_played = myplayermatchstatscount,
        goals = myplayerstats['goals__sum'],
        penaltythrows = myplayerstats['penaltythrows__sum'],
        shots = myplayerstats['shots__sum'],
        saves = myplayerstats['saves__sum'],
        mins = myplayerstats['mins__sum'],
        warn = myplayerstats['warn__sum'],
        dis = myplayerstats['dis__sum'],
        avg_goals = myplayerstats['goals__avg'],
        avg_saves = myplayerstats['saves__avg']
    )





def extract_match_timeline(poolmatch_obj, doc):
    #chrono du match
    two_pages = False

    if doc.page_count == 1:
        #some match don't have a timeline!!!
        return
    
    elif doc.page_count == 2:
        #timeline should be on page 2 but we check
        text = doc[1].get_text()
        if text.startswith('Organisateur'):
            page_chrono = 1
        else:
            #should not happen!!!
            return
    elif doc.page_count == 3:
        #timeline could on page 2 or 3
        text1 = doc[1].get_text()
        text2 = doc[2].get_text()
        if text1.startswith('Organisateur'):
            page_chrono = 1
            two_pages = True
        elif text2.startswith('Organisateur'):
            page_chrono = 2
        else:
            #should not happen!!!
            return
    elif doc.page_count == 4:
        #timeline should be on page 3 and 4
        text = doc[2].get_text()
        if text.startswith('Organisateur'):
            page_chrono = 2
            two_pages = True
        else:
            #should not happen!!!
            return
    else:
        #should not happen!!!
        return
        
    #read first timeline page
    text = doc[page_chrono].get_text()
    
    halftime_index = 0
    time = ''
    score = ''
    description = ''
    prefixes = ['But', 'Arrêt', 'Tir', 'Temps Mort', 'Avertissement', '2MN', 'Disqualification', 'Protocole']
    
    timeline = {}
    timeline['halftimes']=[]

    halftime = {}
    event = {}

    for line in text.splitlines():
        if line.startswith('PERIODE'):
            num = int(re.findall(r'\d|$', line)[0])

            #deal with incorrect repetion of PERIODE
            if num > halftime_index:
                if halftime_index != 0:
                    timeline['halftimes'].append(halftime)

                halftime = {}
                halftime_index +=1
                halftime['index'] = halftime_index
                halftime['events'] = []

        if re.match( r'\d\d[:]\d\d', line) != None:
            time = line
        elif re.match( r'\d\d\s\-\s\d\d', line) != None:
            score = line
        elif line.startswith(tuple(prefixes)):
            description = line
            
            event = {}
            event['time'] = time
            event['score'] = score
            event['desc'] = description

            halftime['events'].append(event)

    

    if two_pages :
        text = doc[page_chrono+1].get_text()

        for line in text.splitlines():
            if line.startswith('PERIODE'):
                num = int(re.findall(r'\d|$', line)[0])

                #deal with incorrect repetion of PERIODE
                if num > halftime_index:
                    if halftime_index != 0:
                        timeline['halftimes'].append(halftime)

                    halftime_index +=1
                    halftime['index'] = halftime_index
                    halftime['events'] = []
                
            elif re.match( r'\d\d[:]\d\d', line) != None:
                time = line
            elif re.match( r'\d\d\s\-\s\d\d', line) != None:
                score = line
            elif line.startswith(tuple(prefixes)):
                description = line

                event['time'] = time
                event['score'] = score
                event['desc'] = description

                halftime['events'].append(event)

    timeline['halftimes'].append(halftime)
    timeline['number'] = halftime_index

    poolmatch_obj.timeline = timeline






def parse_score_sheet_headers (poolmatch_obj, doc):
    #headers
    rec_organisateur = (60, 91, 425, 106)
    rec_competition = (60, 108, 425, 124)
    rec_coderenc = (483, 91, 550, 106)
    rec_groupe =(483, 108, 550, 123)
    rec_score_1 = (483, 125, 516, 141)
    rec_score_2 = (517, 125, 550, 141)
    rec_adresse = (398, 142, 593, 158)
    rec_date = (60, 142, 207, 158)
    rec_journee = (250, 142, 354, 158)
    
    rec_speaker_nom = (60, 159, 249, 170)
    rec_speaker_licence = (250, 159, 297, 170)
    rec_respsalle_nom = (60, 171, 249, 183)
    rec_respsalle_licence = (250, 171, 297, 183)
    rec_chrono_nom = (60, 184, 249, 213)
    rec_chrono_licence = (250, 184, 297, 213)
    rec_secretaire_nom = (60, 212, 249, 224)
    rec_secretaire_licence = (250, 212, 297, 224)
    rec_tuteurtable_nom = (60, 225, 249, 236)
    rec_tuteurtable_licence = (250, 225, 297, 236)
    rec_delegue_nom = (60, 237, 249, 247)
    rec_delegue_licence = (250, 237, 297, 247)
    rec_juge1_nom = (355, 159, 544, 170)
    rec_juge1_licence = (545, 159, 593, 170)
    rec_juge2_nom = (355, 171, 544, 183)
    rec_juge2_licence = (545, 171, 593, 183)
    rec_jugeaccecole_nom = (355, 184, 544, 213)
    rec_jugeaccecole_licence = (545, 184, 593, 213)
    rec_jugeacc_nom = (355, 212, 544, 224)
    rec_jugeacc_licence = (545, 212, 593, 224)
    rec_jugesup_nom = (355, 225, 544, 236)
    rec_jugesup_licence = (545, 225, 593, 236)
    rec_jugedelegue_nom = (355, 237, 544, 247)
    rec_jugedelegue_licence = (545, 237, 593, 247)
    
    
    organisateur = doc[0].get_textbox(rec_organisateur)
    competition = doc[0].get_textbox(rec_competition)
    coderenc = doc[0].get_textbox(rec_coderenc)
    groupe = doc[0].get_textbox(rec_groupe)
    score_1 = doc[0].get_textbox(rec_score_1)
    score_2 = doc[0].get_textbox(rec_score_2)
    adresse = doc[0].get_textbox(rec_adresse)
    date = doc[0].get_textbox(rec_date)
    journee = doc[0].get_textbox(rec_journee)
    
    speaker_nom = doc[0].get_textbox(rec_speaker_nom)
    speaker_licence = doc[0].get_textbox(rec_speaker_licence)
    respsalle_nom = doc[0].get_textbox(rec_respsalle_nom)
    respsalle_licence = doc[0].get_textbox(rec_respsalle_licence)
    chrono_nom = doc[0].get_textbox(rec_chrono_nom)
    chrono_licence = doc[0].get_textbox(rec_chrono_licence)
    secretaire_nom = doc[0].get_textbox(rec_secretaire_nom)
    secretaire_licence = doc[0].get_textbox(rec_secretaire_licence)
    tuteurtable_nom = doc[0].get_textbox(rec_tuteurtable_nom)
    tuteurtable_licence = doc[0].get_textbox(rec_tuteurtable_licence)
    delegue_nom = doc[0].get_textbox(rec_delegue_nom)
    delegue_licence = doc[0].get_textbox(rec_delegue_licence)
    juge1_nom = doc[0].get_textbox(rec_juge1_nom)
    juge1_licence = doc[0].get_textbox(rec_juge1_licence)
    juge2_nom = doc[0].get_textbox(rec_juge2_nom)
    juge2_licence = doc[0].get_textbox(rec_juge2_licence)
    jugeaccecole_nom = doc[0].get_textbox(rec_jugeaccecole_nom)
    jugeaccecole_licence = doc[0].get_textbox(rec_jugeaccecole_licence)
    jugeacc_nom = doc[0].get_textbox(rec_jugeacc_nom)
    jugeacc_licence = doc[0].get_textbox(rec_jugeacc_licence)
    jugesup_nom = doc[0].get_textbox(rec_jugesup_nom)
    jugesup_licence = doc[0].get_textbox(rec_jugesup_licence)
    jugedelegue_nom = doc[0].get_textbox(rec_jugedelegue_nom)
    jugedelegue_licence = doc[0].get_textbox(rec_jugedelegue_licence)


    #update competition
    poolmatch_obj.pool.phase.competition.age = groupe[5:7]
    poolmatch_obj.pool.phase.competition.gender = groupe[0:1]
    poolmatch_obj.pool.phase.competition.save()

    #update pool
    #TODO ???

    #update match
    officials = {}
    officials['speaker'] = {}
    officials['speaker']['name'] = speaker_nom
    officials['speaker']['licence'] = speaker_licence
    officials['respsalle'] = {}
    officials['respsalle']['name'] = respsalle_nom
    officials['respsalle']['licence'] = respsalle_licence
    officials['chrono'] = {}
    officials['chrono']['name'] = chrono_nom
    officials['chrono']['licence'] = chrono_licence
    officials['secretaire'] = {}
    officials['secretaire']['name'] = secretaire_nom
    officials['secretaire']['licence'] = secretaire_licence
    officials['tuteurtable'] = {}
    officials['tuteurtable']['name'] = tuteurtable_nom
    officials['tuteurtable']['licence'] = tuteurtable_licence
    officials['delegue'] = {}
    officials['delegue']['name'] = delegue_nom
    officials['delegue']['licence'] = delegue_licence
    officials['juge1'] = {}
    officials['juge1']['name'] = juge1_nom
    officials['juge1']['licence'] = juge1_licence
    officials['juge2'] = {}
    officials['juge2']['name'] = juge2_nom
    officials['juge2']['licence'] = juge2_licence
    officials['jugeaccecole'] = {}
    officials['jugeaccecole']['name'] = jugeaccecole_nom
    officials['jugeaccecole']['licence'] = jugeaccecole_licence
    officials['jugeacc'] = {}
    officials['jugeacc']['name'] = jugeacc_nom
    officials['jugeacc']['licence'] = jugeacc_licence
    officials['jugesup'] = {}
    officials['jugesup']['name'] = jugesup_nom
    officials['jugesup']['licence'] = jugesup_licence
    officials['jugedelegue'] = {}
    officials['jugedelegue']['name'] = jugedelegue_nom
    officials['jugedelegue']['licence'] = jugedelegue_licence
    
    #poolmatch_obj.officials = json.dumps(officials)
    poolmatch_obj.officials = officials

    #update gym
    poolmatch_obj.gym.location = adresse
    poolmatch_obj.gym.save()


def parse_score_sheet_team(poolmatch_obj, team, team_nb, page, Y_INIT, Y_INTER):

    vide = 0
    nb_joueurs = 0

    nb_line = int((Y_INTER - Y_INIT)/11)
    Y_THICKNESS = (Y_INTER - Y_INIT)/nb_line
    
    MARGIN = 2 #player info localization is approximative
    
    for i in range(0,nb_line):
        rec_capitanat = (60, (Y_INIT+i*Y_THICKNESS)+MARGIN,79,(Y_INIT+(i+1)*Y_THICKNESS)-MARGIN)
        rec_numero = (80, (Y_INIT+i*Y_THICKNESS)+MARGIN,99,(Y_INIT+(i+1)*Y_THICKNESS)-MARGIN)
        rec_nom = (100, (Y_INIT+i*Y_THICKNESS)+MARGIN,334,(Y_INIT+(i+1)*Y_THICKNESS)-MARGIN)
        rec_licence = (335, (Y_INIT+i*Y_THICKNESS)+MARGIN,391,(Y_INIT+(i+1)*Y_THICKNESS)-MARGIN)

        rec_typelicence = (392, (Y_INIT+i*Y_THICKNESS)+MARGIN,416,(Y_INIT+(i+1)*Y_THICKNESS)-MARGIN)
        rec_buts = (417, (Y_INIT+i*Y_THICKNESS)+MARGIN,441,(Y_INIT+(i+1)*Y_THICKNESS)-MARGIN)
        rec_7m = (443, (Y_INIT+i*Y_THICKNESS)+MARGIN,467,(Y_INIT+(i+1)*Y_THICKNESS)-MARGIN)
        rec_tirs = (468, (Y_INIT+i*Y_THICKNESS)+MARGIN,493,(Y_INIT+(i+1)*Y_THICKNESS)-MARGIN)
        rec_arrets = (494, (Y_INIT+i*Y_THICKNESS)+MARGIN,518,(Y_INIT+(i+1)*Y_THICKNESS)-MARGIN)
        rec_avert = (519, (Y_INIT+i*Y_THICKNESS)+MARGIN,533,(Y_INIT+(i+1)*Y_THICKNESS)-MARGIN)
        rec_2mn = (534, (Y_INIT+i*Y_THICKNESS)+MARGIN,550,(Y_INIT+(i+1)*Y_THICKNESS)-MARGIN)
        rec_dis = (551, (Y_INIT+i*Y_THICKNESS)+MARGIN,569,(Y_INIT+(i+1)*Y_THICKNESS)-MARGIN)

        capitanat = page.get_textbox(rec_capitanat)
        numero = page.get_textbox(rec_numero)
        nom = page.get_textbox(rec_nom)
        licence = page.get_textbox(rec_licence)
        typelicence = page.get_textbox(rec_typelicence)
        buts = page.get_textbox(rec_buts)
        _7m = page.get_textbox(rec_7m)
        tirs = page.get_textbox(rec_tirs)
        arrets = page.get_textbox(rec_arrets)
        avert = page.get_textbox(rec_avert)
        _2mn = page.get_textbox(rec_2mn)
        dis = page.get_textbox(rec_dis)

        if numero == '':
            vide += 1
        else :
            nb_joueurs = i+1
            
            if numero != '' :
                
                player_obj, created = Player.objects.update_or_create(
                    id=licence,
                    defaults = {
                        'club' : team.club,
                        'first_name' : re.search('[a-z]+([\-\'\ ]*[a-z]+)*', nom).group(0).strip(),
                        'last_name' : re.search('[A-Z]+([\-\'\ ]*[A-Z]+)*', nom).group(0).strip(),
                        'gender' : 'M' if (licence[7:8] == '1') else 'F'
                    }
                )

                pool_player_stat_id = poolmatch_obj.pool.id+"_"+str(poolmatch_obj.day.index)+"_"+licence
                                                    
                PlayerMatchStat.objects.update_or_create(
                    id=pool_player_stat_id,
                    defaults = {
                        'player' : player_obj,
                        'pool' : poolmatch_obj.pool,
                        'match' : poolmatch_obj,
                        'goals' : int(buts or 0),
                        'penaltythrows' : int(_7m or 0),
                        'shots' : int(tirs or 0),
                        'saves' : int(arrets or 0),
                        'mins' : int(_2mn or 0),
                        'warn' : 1 if (avert == 'X') else 0,
                        'dis' : 1 if (dis == 'X') else 0
                    }
                )

                #update player pool stats
                update_player_pool_stats(player_obj, poolmatch_obj.pool)

                #update player stats
                update_player_stats(player_obj)



        
    idx_coach = nb_joueurs + vide
    
    rec_offica_nom = (100, (Y_INIT+idx_coach*Y_THICKNESS+MARGIN),334,(Y_INIT+(idx_coach+1)*Y_THICKNESS-MARGIN))
    rec_offica_licence = (335, (Y_INIT+idx_coach*Y_THICKNESS+MARGIN),391,(Y_INIT+(idx_coach+1)*Y_THICKNESS-MARGIN))
    rec_officb_nom = (100, (Y_INIT+(idx_coach+1)*Y_THICKNESS)+MARGIN,334,(Y_INIT+(idx_coach+2)*Y_THICKNESS-MARGIN))
    rec_officb_licence = (335, (Y_INIT+(idx_coach+1)*Y_THICKNESS+MARGIN),391,(Y_INIT+(idx_coach+2)*Y_THICKNESS-MARGIN))
    rec_officc_nom = (100, (Y_INIT+(idx_coach+2)*Y_THICKNESS+MARGIN),334,(Y_INIT+(idx_coach+3)*Y_THICKNESS-MARGIN))
    rec_officc_licence = (335, (Y_INIT+(idx_coach+2)*Y_THICKNESS+MARGIN),391,(Y_INIT+(idx_coach+3)*Y_THICKNESS-MARGIN))
    rec_officd_nom = (100, (Y_INIT+(idx_coach+3)*Y_THICKNESS+MARGIN),334,(Y_INIT+(idx_coach+4)*Y_THICKNESS-MARGIN))
    rec_officd_licence = (335, (Y_INIT+(idx_coach+3)*Y_THICKNESS+MARGIN),391,(Y_INIT+(idx_coach+4)*Y_THICKNESS-MARGIN))
    rec_kine_nom = (100, (Y_INIT+(idx_coach+4)*Y_THICKNESS+MARGIN),334,(Y_INIT+(idx_coach+5)*Y_THICKNESS-MARGIN))
    rec_kine_licence = (335, (Y_INIT+(idx_coach+4)*Y_THICKNESS+MARGIN),391,(Y_INIT+(idx_coach+5)*Y_THICKNESS-MARGIN))
    rec_medecin_nom = (100, (Y_INIT+(idx_coach+5)*Y_THICKNESS+MARGIN),334,(Y_INIT+(idx_coach+6)*Y_THICKNESS-MARGIN))
    rec_medecin_licence = (335, (Y_INIT+(idx_coach+5)*Y_THICKNESS+MARGIN),391,(Y_INIT+(idx_coach+6)*Y_THICKNESS-MARGIN))
    
    offica_nom = page.get_textbox(rec_offica_nom)
    offica_licence = page.get_textbox(rec_offica_licence)
    officb_nom = page.get_textbox(rec_officb_nom)
    officb_licence = page.get_textbox(rec_officb_licence)
    officc_nom = page.get_textbox(rec_officc_nom)
    officc_licence = page.get_textbox(rec_officc_licence)
    officd_nom = page.get_textbox(rec_officd_nom)
    officd_licence = page.get_textbox(rec_officd_licence)
    kine_nom = page.get_textbox(rec_kine_nom)
    kine_licence = page.get_textbox(rec_kine_licence)
    medecin_nom = page.get_textbox(rec_medecin_nom)
    medecin_licence = page.get_textbox(rec_medecin_licence)


    team_offic = {}
    team_offic['offica'] = {}
    team_offic['offica']['name'] = offica_nom
    team_offic['offica']['licence'] = offica_licence
    team_offic['officb'] = {}
    team_offic['officb']['name'] = officb_nom
    team_offic['officb']['licence'] = officb_licence
    team_offic['officc'] = {}
    team_offic['officc']['name'] = officc_nom
    team_offic['officc']['licence'] = officc_licence
    team_offic['officd'] = {}
    team_offic['officd']['name'] = officd_nom
    team_offic['officd']['licence'] = officd_licence
    team_offic['kine'] = {}
    team_offic['kine']['name'] = kine_nom
    team_offic['kine']['licence'] = kine_licence
    team_offic['medecin'] = {}
    team_offic['medecin']['name'] = medecin_nom
    team_offic['medecin']['licence'] = medecin_licence
    
    if team_nb == 1:
        poolmatch_obj.team_1_officials = team_offic
    elif team_nb == 2:
        poolmatch_obj.team_2_officials = team_offic

    
    #update team
    rec_code_club = (2, Y_INIT-12, 25, Y_INIT-12+47)
    code_club = page.get_textbox(rec_code_club)

    team.club.code = code_club
    team.club.region = code_club[0:2]
    team.club.departement = code_club[2:4]
    team.club.save()

def get_and_parse_match_sheet(poolmatch_obj):

    fdm_base_url = "https://media-ffhb-fdm.ffhandball.fr/fdm/"
    
    fdm = poolmatch_obj.fdm
    fdm_url = fdm_base_url + fdm[0] + "/" + fdm[1] + "/" + fdm[2] + "/" + fdm[3] + "/" + fdm + ".pdf"

    #fdm_url = 'https://media-ffhb-fdm.ffhandball.fr/fdm/S/A/E/K/SAEKWQI.pdf'

    print(fdm_url)
    
    try:
        r = requests.get(fdm_url)
    except requests.exceptions.RequestException as e:
        print("Error requesting fdm url")
        print(e)
    else:
        
        if r.headers['Content-Type'] != 'application/pdf':
            return #some match don't have as match sheet !!!

        mem_area = io.BytesIO(r.content)
        doc = fitz.open(stream=mem_area, filetype="pdf")

        #parse headers
        parse_score_sheet_headers(poolmatch_obj, doc)

        #search anchors in score sheet
        prenom_list = doc[0].search_for("prénom")
        resp_list = doc[0].search_for("Officiel Resp")

        if len(prenom_list) == 2:
            #normal case with team up to 16 players
            Y_INIT1 = prenom_list[0][1] + 10
            Y_INIT2 = prenom_list[1][1] + 10

            Y_INTER1 = resp_list[0][1] - 2
            Y_INTER2 = resp_list[1][1] - 2

            parse_score_sheet_team(poolmatch_obj, poolmatch_obj.team_1, 1, doc[0], Y_INIT1, Y_INTER1)
            parse_score_sheet_team(poolmatch_obj, poolmatch_obj.team_2, 2, doc[0], Y_INIT2, Y_INTER2)

        elif len(prenom_list) == 1 :
            #unusual case with team1 with more than 16 players, team2 is on doc[1]
            Y_INIT1 = prenom_list[0][1] + 10
            Y_INTER1 = resp_list[0][1] - 2
            

            #search prenom in sheet 2
            prenom_list = doc[1].search_for("prénom")
            resp_list = doc[1].search_for("Officiel Resp")
            Y_INIT2 = prenom_list[0][1] + 10
            Y_INTER2 = resp_list[0][1] - 2

            parse_score_sheet_team(poolmatch_obj, poolmatch_obj.team_1, 1, doc[0], Y_INIT1, Y_INTER1)
            parse_score_sheet_team(poolmatch_obj, poolmatch_obj.team_2, 2, doc[1], Y_INIT2, Y_INTER2)

        else:
            #should not happen
            return
        
        #extract match timeline
        extract_match_timeline(poolmatch_obj, doc )

        #save the match in the database
        poolmatch_obj.save()

        



    


def decypher( text, data_cfk):
    result = bytes()
    key = data_cfk.encode('utf-8')
    keylen = len(key)
    data = base64.b64decode(text)
    datalen = len(data)

    for i in range(datalen):
        result += (data[i] ^ key[i % keylen]).to_bytes( 1, 'little')
    
    return result.decode('utf-8')

def get_data_cfk():
    #get data-cfk to decypher api response
    try:
        response = requests.get("https://www.ffhandball.fr/")
    except requests.exceptions.RequestException as e:
        print("Error requesting main url")
        raise
    else:
        soup = BeautifulSoup(response.content, "html.parser")
        body = soup.find_all("body")
        data_cfk = body[0]['data-cfk']

    return data_cfk

def get_championships( season, category, data_cfk):
    #get championships and decypher the api response
    url = (base_url 
        + "?block=competitions---competition-main-menu"
        + "&ext_saison_id=" + season
        + "&url_competition_type=" + category)
    
    #print(url)

    try:
        response_enc = requests.get( url )
    except requests.exceptions.RequestException as e:
        print("Error requesting championships url")
        raise
    else:
        response_dec = decypher( response_enc.text, data_cfk)
        return json.loads(response_dec)

def get_competitions( season, category, libelle, ext_structure_id, data_cfk):
    #get competitions and decypher the api response
    structure_url = 'o' + libelle.lower().replace( ' ', '-') + '-' + ext_structure_id

    url = (base_url 
        +"?block=competitions---competition-main-menu"
        + "&ext_saison_id="  + season
        + "&url_competition_type="  + category
        + "&url_structure=" + structure_url)
    
    #print(url)


    try:
        response_enc = requests.get( url )
    except requests.exceptions.RequestException as e:
        print("Error requesting competitions url")
        raise
    else:
        response_dec = decypher( response_enc.text, data_cfk)
        return json.loads(response_dec)

def get_phases_and_pools( season, category, competition_libelle, ext_competition_id, data_cfk):
    #get phases and pools and decypher the api response
    competition_url = 'o' + competition_libelle.lower().replace( ' ', '-').replace( '--', '-') + '-' + ext_competition_id

    url = (base_url 
        +"?block=competitions---poule-selector"
        + "&ext_saison_id="  + season
        + "&url_competition_type="  + category
        + "&url_competition=" + competition_url)
    
    #print(url)

    try:
        response_enc = requests.get( url )
    except requests.exceptions.RequestException as e:
        print("Error requesting phases and pools url")
        raise
    else:
        response_dec = decypher( response_enc.text, data_cfk)
        return json.loads(response_dec)
    
def get_pooldays_and_poolteams( season, category, competition_libelle, ext_competition_id, ext_pool_id, data_cfk):
    #get pooldays and teams and decypher the api response
    competition_url = 'o' + competition_libelle.lower().replace( ' ', '-').replace( '--', '-') + '-' + ext_competition_id

    url = (base_url 
        +"?block=competitions---poule-selector"
        + "&ext_saison_id="  + season
        + "&url_competition_type="  + category
        + "&url_competition=" + competition_url
        + "&ext_poule_id=" + ext_pool_id)
    
    #print(url)

    try:
        response_enc = requests.get( url )
    except requests.exceptions.RequestException as e:
        print("Error requesting matches url")
        raise
    else:
        response_dec = decypher( response_enc.text, data_cfk)
        return json.loads(response_dec)

def get_matches( season, category, competition_libelle, ext_competition_id, ext_pool_id, poolday_index, data_cfk):
    #get matches and decypher the api response
    competition_url = 'o' + competition_libelle.lower().replace( ' ', '-').replace( '--', '-') + '-' + ext_competition_id

    url = (base_url 
        +"?block=competitions---rencontre-list"
        + "&ext_saison_id="  + season
        + "&url_competition_type="  + category
        + "&url_competition=" + competition_url
        + "&ext_poule_id=" + ext_pool_id
        + "&numero_journee=" + poolday_index)
    
    #print(url)

    try:
        response_enc = requests.get( url )
    except requests.exceptions.RequestException as e:
        print("Error requesting matches url")
        raise
    else:
        response_dec = decypher( response_enc.text, data_cfk)
        return json.loads(response_dec)

def get_ranking( season, category, competition_libelle, ext_competition_id, ext_pool_id, data_cfk):
    #get ranking and decypher the api response
    competition_url = 'o' + competition_libelle.lower().replace( ' ', '-').replace( '--', '-') + '-' + ext_competition_id

    url = (base_url 
        +"?block=competitions---mini-classement-or-ads"
        + "&ext_saison_id="  + season
        + "&url_competition_type="  + category
        + "&url_competition=" + competition_url
        + "&ext_poule_id=" + ext_pool_id)
    
    #print(url)

    try:
        response_enc = requests.get( url )
    except requests.exceptions.RequestException as e:
        print("Error requesting ranking url")
        raise
    else:
        response_dec = decypher( response_enc.text, data_cfk)
        return json.loads(response_dec)


def scrap( season, category):

    tz = get_current_timezone()

    #get data-cfk to decypher api response
    try:
        data_cfk = get_data_cfk()
    except requests.exceptions.RequestException:
        print("Error getting cfk")
        return
    
    #get championships
    try:
        data_championships = get_championships( season, category, data_cfk)
    except requests.exceptions.RequestException:
        print("Error getting championships")
        return
    else:
        for championship in data_championships['structures']:
            # creating a new championship
            championship_libelle = championship['libelle']
            
            print("--- Updating "+ championship_libelle)

            if category == 'departemental':
                category_abr = 'DEP'
            elif category == 'regional':
                category_abr = 'REG'
            else:
                #TODO completer les categories
                return
            
            championship_obj, created = Championship.objects.update_or_create(
                id = championship['id'],
                defaults = {
                    'season' : season,
                    'category' : category_abr,
                    'name' : championship['libelle'],
                    'acronym' : championship['sigle'],
                    'type' : championship['type'],
                    'code' : championship['code'],
                    'region' : championship['code'][0:2],
                    'departement' : championship['code'][2:4],
                    'logo' : championship['logo']
                }
            )

            #get competitions
            try:
                data_competitions = get_competitions( season, category, championship_libelle, championship['ext_structureId'], data_cfk)
            except requests.exceptions.RequestException as e:
                print("Error getting competitions")
            else:

                for competition in data_competitions['competitions']:
                    # creating a new championship
                    competition_libelle = competition['libelle']
                    last_update = datetime.strptime(competition['dateDernierUpdateEnfants'], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=tz)
                    
                    print("--- --- Updating " + competition_libelle)

                    try:
                        competition_obj = Competition.objects.get(pk=competition['id'])
                    except Competition.DoesNotExist:
                        competition_obj = None

                    if competition_obj :
                        known_last_update = competition_obj.last_update
                    else :
                        known_last_update = datetime(2000, 1, 1, 00, 00, 00, 000, tzinfo=tz)

                    competition_obj, created = Competition.objects.update_or_create(
                        id = competition['id'],
                        defaults = {
                            'championship' : championship_obj,
                            'name' : competition['libelle'],
                            'gender' : competition['genre'],
                            'logo' : competition['logo'],
                            'last_update' : last_update
                        }
                    )

                    if last_update > known_last_update :

                        #get phases and pools
                        try:
                            data_phases_and_pools = get_phases_and_pools( season, category, competition_libelle, competition['ext_competitionId'], data_cfk)
                        except requests.exceptions.RequestException as e:
                            print("Error getting phases and pools")
                        else:

                            for phase in data_phases_and_pools['phases']:
                                # creating a new phase
                                phase_libelle = phase['libelle']
                                last_update = datetime.strptime(phase['dateDernierUpdateEnfants'], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=tz)
                                
                                print("--- --- --- Updating phase " + phase_libelle)

                                phase_obj, created = Phase.objects.update_or_create(
                                    id = phase['id'],
                                    defaults = {
                                        'competition' : competition_obj,
                                        'name' : phase['libelle'],
                                        'last_update' : last_update
                                    }
                                )

                            for pool in data_phases_and_pools['poules']:
                                # creating a new pool
                                pool_libelle = pool['libelle']
                                last_update = datetime.strptime(pool['dateDernierUpdateEnfants'], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=tz)
                                phase_obj = Phase.objects.get(pk=pool['phaseId'])
                                
                                print("--- --- --- Updating pool " + pool_libelle)

                                try:
                                    pool_obj = Pool.objects.get(pk=pool['id'])
                                except Pool.DoesNotExist:
                                    pool_obj = None

                                if pool_obj :
                                    known_last_update = pool_obj.last_update
                                else :
                                    known_last_update = datetime(2000, 1, 1, 00, 00, 00, 000, tzinfo=tz)

                                pool_obj, created = Pool.objects.update_or_create(
                                    id = pool['id'],
                                    defaults = {
                                        'phase' : phase_obj,
                                        'name' : pool['libelle'],
                                        'last_update' : last_update
                                    }
                                )

                                print(last_update)
                                print(known_last_update)

                                if last_update > known_last_update :

                                    #get pooldays and teams
                                    try:
                                        data_pooldays_and_poolteams = get_pooldays_and_poolteams( season, category, competition_libelle, competition['ext_competitionId'], pool['ext_pouleId'], data_cfk)
                                    except requests.exceptions.RequestException as e:
                                        print("Error getting pooldays and teams")
                                    else:
                                        #teams
                                        data_poolteams = data_pooldays_and_poolteams['equipe_options']
                                        for poolteam in data_poolteams:
                                            #create or update a club
                                            # try:
                                            #     club_obj = Club.objects.get(pk=poolteam['structureId'])
                                            #     club_obj.name = os.path.commonprefix([club_obj.name, poolteam['libelle']])
                                            #     club_obj.save()
                                                
                                            # except Club.DoesNotExist:
                                            Club.objects.update_or_create(
                                                id = poolteam['structureId'],
                                                defaults = {
                                                    'name' : poolteam['libelle'],
                                                    # other fields are left empty
                                                    # they will be filled when scraping match sheet
                                                }
                                            )
                                            
                                            # creating a new team
                                            poolteam_libelle = poolteam['libelle']
                                            club_obj = Club.objects.get(pk=poolteam['structureId'])
                                            
                                            print("--- --- --- --- Updating poolteam " + poolteam_libelle)

                                            PoolTeam.objects.update_or_create(
                                                id = poolteam['id'],
                                                defaults = {
                                                    'pool' : pool_obj,
                                                    'club' : club_obj,
                                                    'name' : poolteam['libelle']
                                                    # other fields are left empty
                                                }
                                            )
                                        
                                    

                                        #pooldays
                                        data_pooldays = json.loads(data_pooldays_and_poolteams['selected_poule']['journees'])
                                        for poolday in data_pooldays:
                                            # creating a new poolday
                                            poolday_index = str(poolday['journee_numero'])
                                            poolday_id = pool['ext_pouleId'] + "_" + poolday_index
                                            
                                            if poolday['date_debut'] != None :
                                                start = date.fromisoformat(str(poolday['date_debut']))
                                            else :
                                                start = None
                                            
                                            if poolday['date_fin'] != None :
                                                finish = date.fromisoformat(str(poolday['date_fin']))
                                            else :
                                                finish = None
                                            
                                            print("--- --- --- --- Updating poolday J" + poolday_index)

                                            poolday_obj, created = PoolDay.objects.update_or_create(
                                                id = poolday_id,
                                                defaults = {
                                                    'pool' : pool_obj,
                                                    'index' : poolday_index,
                                                    'start' : start,
                                                    'finish' : finish
                                                }
                                            )

                                            #get matches
                                            try:
                                                data_matches = get_matches( season, category, competition_libelle, competition['ext_competitionId'], pool['ext_pouleId'], poolday_index, data_cfk)
                                            except requests.exceptions.RequestException as e:
                                                print("Error getting matches")
                                            else:
                                                for match in data_matches['rencontres']:
                                                    #creating a new gym
                                                    if match['equipementId'] != None : 
                                                        gym_obj , created = Gym.objects.update_or_create(
                                                            id = match['equipementId'],
                                                            defaults = {
                                                                # other fields are left empty
                                                                # they will be filled when scraping match sheet
                                                            }
                                                        )
                                                    else :
                                                        gym_obj = None
                                                    
                                                    # creating a new match
                                                    ext_match_id = match['ext_rencontreId']
                                                    team1_id = match['equipe1Id']
                                                    team2_id = match['equipe2Id']
                                                    team1_obj = PoolTeam.objects.get(pk=match['equipe1Id'])
                                                    team2_obj = PoolTeam.objects.get(pk=match['equipe2Id'])
                                                    if match['date'] != None :
                                                        date_match = datetime.strptime(match['date'], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=tz)
                                                    else :
                                                        date_match = None

                                                    print("--- --- --- --- --- Updating match " + ext_match_id + " : " + team1_obj.name + " - " + team2_obj.name)

                                                    match_played = not (match['equipe1Score'] == None or match['equipe2Score'] == None or match['equipe1Score'] == 'FO' or match['equipe2Score'] == 'FO' )

                                                    try:
                                                        poolmatch_obj = PoolMatch.objects.get(id = match['id'])
                                                    except PoolMatch.DoesNotExist:
                                                        poolmatch_obj = PoolMatch.objects.create(
                                                            id = match['id'],
                                                            pool = pool_obj,
                                                            day = poolday_obj,
                                                            date = date_match,
                                                            played = match_played,
                                                            team_1 = team1_obj,
                                                            team_1_score = match['equipe1Score'],
                                                            team_1_score_ht = match['equipe1ScoreMT'],
                                                            team_2 = team2_obj,
                                                            team_2_score = match['equipe2Score'],
                                                            team_2_score_ht = match['equipe2ScoreMT'],
                                                            fdm = match['fdmCode'],
                                                            gym = gym_obj
                                                        )
                                                    else:
                                                        #get previous match state to update only if necessary
                                                        match_already_played = poolmatch_obj.played
                                                        
                                                        poolmatch_obj.pool = pool_obj
                                                        poolmatch_obj.day = poolday_obj
                                                        poolmatch_obj.date = date_match
                                                        poolmatch_obj.played = match_played
                                                        poolmatch_obj.team_1 = team1_obj
                                                        poolmatch_obj.team_1_score = match['equipe1Score']
                                                        poolmatch_obj.team_1_score_ht = match['equipe1ScoreMT']
                                                        poolmatch_obj.team_2 = team2_obj
                                                        poolmatch_obj.team_2_score = match['equipe2Score']
                                                        poolmatch_obj.team_2_score_ht = match['equipe2ScoreMT']
                                                        poolmatch_obj.fdm = match['fdmCode']
                                                        poolmatch_obj.gym = gym_obj
                                                        
                                                        poolmatch_obj.save()

                                                    #updating clubs logo
                                                    team1_obj.club.logo = match['structure1Logo']
                                                    team1_obj.club.save()
                                                    team2_obj.club.logo = match['structure2Logo']
                                                    team2_obj.club.save()

                                                    #parse match sheet only if necessary
                                                    if match_played and (not match_already_played):
                                                        get_and_parse_match_sheet(poolmatch_obj)
                                    
                                    #get pool ranking
                                    try:
                                        data_ranking = get_ranking( season, category, competition_libelle, competition['ext_competitionId'], pool['ext_pouleId'], data_cfk)
                                    except requests.exceptions.RequestException as e:
                                        print("Error getting ranking")
                                    else:
                                        data_teamrankings = data_ranking['classements']

                                        if data_teamrankings != None:
                                            for data_teamranking in data_teamrankings:
                                                #create a ranking for a pool team
                                                poolteam_libelle = data_teamranking['equipe_libelle']
                                                
                                                print("--- --- --- --- Updating ranking for team " + poolteam_libelle)

                                                #Pool team is supposed to already exists
                                                poolmatch_obj = PoolTeam.objects.get(pk=data_teamranking['equipeId'])

                                                poolmatch_obj.ranking = int(data_teamranking['place'])
                                                poolmatch_obj.points = int(data_teamranking['point'])
                                                poolmatch_obj.games = int(data_teamranking['joue'])
                                                poolmatch_obj.wins = int(data_teamranking['gagne'])
                                                poolmatch_obj.draws = int(data_teamranking['nul'])
                                                poolmatch_obj.defeats = int(data_teamranking['perdu'])
                                                poolmatch_obj.scored = int(data_teamranking['butPlus'])
                                                poolmatch_obj.missed = int(data_teamranking['butMoins'])
                                                poolmatch_obj.difference = int(data_teamranking['diff'])
                                                poolmatch_obj.last_results = data_teamranking['dernieresRencontres']
                                                poolmatch_obj.save()



class Command(BaseCommand):
    args = ''
    help = 'Update database'

    def handle(self, *args, **options):

        # scrap championnats departementaux
        scrap( '19', 'departemental')
        # scrap championnats regionaux
        scrap( '19', 'regional')
        #national
        #TODO
        
    