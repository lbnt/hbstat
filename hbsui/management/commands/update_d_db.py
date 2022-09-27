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

import requests
import json
import hashlib

base_url = "https://jjht57whqb.execute-api.us-west-2.amazonaws.com/prod"


def scrap(category):

    url_championship = base_url+"/championship/"+category
    
    try:
        response_championship = requests.get(url_championship)
    except requests.exceptions.RequestException as e:
        print("Error requesting championships url")
    else:
        data_championship = json.loads(response_championship.text)

        for championship in data_championship['events']:
            # create a new championship
            print("--- Updating "+championship['eventName'])
            championship_obj, created = DChampionship.objects.update_or_create(
                id=championship['eventId'],
                defaults = {
                    'category' : category,
                    'name' : championship['eventName'],
                    'code' : championship['champCode']
                }
            )
            
            url_competition = base_url+"/competition/"+championship['champCode']
            try:
                response_competition = requests.get(url_competition)
            except requests.exceptions.RequestException as e:
                print("Error requesting competitions url")
            else:

                data_competition = json.loads(response_competition.text)

                for competition in data_competition['events']:
                    # create a new competition
                    print("--- --- Updating "+competition['eventName'])
                    
                    competition_obj, created = DCompetition.objects.update_or_create(
                        id=competition['eventId'],
                        defaults = {
                            'championship' : championship_obj,
                            'name' : competition['eventName']
                        }
                    )
                    
                    url_pools = base_url+"/competitionPool/"+competition['eventId']
                    try:
                        response_pools = requests.get(url_pools)
                    except requests.exceptions.RequestException as e:
                        print("Error requesting pools url " + url_pools)
                    else:
                        data_pools = json.loads(response_pools.text)

                        for pool in data_pools['pools']:
                            
                            # create or update pool
                            print("--- --- --- Updating "+pool['phaseName']+" - "+pool['poolName'])
                            pool_obj, created = DPool.objects.update_or_create(
                                id=str(pool['poolId']),
                                defaults = {
                                    'competition' : competition_obj,
                                    'phase_name' : pool['phaseName'],
                                    'name' : pool['poolName'],
                                    'code' : pool['poolCode'],
                                    'age' : pool['poolCode'][5:7],
                                    'gender' : pool['poolCode'][0:1],
                                    # player_hash not modified, empty if created
                                    # pool_hash not modified, empty if created
                                }
                            )

                            #download pool details : dates, pool players, pool teams
                            url_pool = base_url+"/pool/"+str(pool['poolId'])
                            try:                                
                                response_pool = requests.get(url_pool)
                            except requests.exceptions.RequestException as e:
                                print("Error requesting pools url " + url_pool)
                            else:
                                data_pool = json.loads(response_pool.text)
                                
                                #compute file hash
                                data_pool_hash = hashlib.md5(response_pool.text.encode("utf-8")).hexdigest()
                                
                                #if pool details has changed, parse and record file
                                if pool_obj.pool_hash != data_pool_hash :
                                    # update pool with new pool data hash
                                    print("--- --- --- New pool hash: "+ data_pool_hash + ", old: " + pool_obj.pool_hash )
                                    pool_obj.pool_hash = data_pool_hash
                                    pool_obj.save()


                                    #pool dates
                                    data_pool_dates_keys = data_pool['dates'].keys()
                                    for index_pool_date in data_pool_dates_keys:
                                        # create a new pool date
                                        pool_date = data_pool['dates'][index_pool_date]
                                        print("--- --- --- Updating "+pool_date['start']+" to "+pool_date['finish'])
                                        pool_date_id = str(pool['poolId'])+"_"+str(index_pool_date)
                                        
                                        pool_date_obj, created = DPoolDate.objects.update_or_create(
                                            id=pool_date_id,
                                            defaults = {
                                                'pool' : pool_obj,
                                                'start' : pool_date['start'],
                                                'finish' : pool_date['finish']
                                            }
                                        )
                                        
                                        index_pool_event = 0
                                        for pool_event in pool_date['events']:
                                            # create a new pool event
                                            print("--- --- --- --- Updating event "+str(index_pool_event)+" at "+pool_date['start']+" to "+pool_date['finish'])
                                            pool_event_id = str(pool['poolId'])+"_"+index_pool_date+"_"+str(index_pool_event)
                                            pool_event_code = pool_event['CON_CODE_RENC']
                                            pool_event_fdm = "https://www.ffhandball.fr/api/s3/fdm/"+pool_event_code[0:1]+"/"+pool_event_code[1:2]+"/"+pool_event_code[2:3]+"/"+pool_event_code[3:4]+"/"+pool_event_code+".pdf"

                                            DPoolEvent.objects.update_or_create(
                                                id=pool_event_id,
                                                defaults = {
                                                    'pool' : pool_obj,
                                                    'date' : pool_date_obj,
                                                    'date_day' : pool_event['date']['day'],
                                                    'date_date' : pool_event['date']['date'],
                                                    'date_hour' : pool_event['date']['hour'],
                                                    'date_minute' : pool_event['date']['minute'],
                                                    'team_0_name' : pool_event['teams'][0]['name'],
                                                    'team_0_score' : pool_event['teams'][0]['score'],
                                                    'team_1_name' : pool_event['teams'][1]['name'],
                                                    'team_1_score' : pool_event['teams'][1]['score'],
                                                    'referee_0_name' : pool_event['referees'][0]['name'],
                                                    'referee_1_name' : pool_event['referees'][1]['name'],
                                                    'location_0' : pool_event['location'][0],
                                                    'location_1' : pool_event['location'][1],
                                                    'location_2' : pool_event['location'][2],
                                                    'code' : pool_event['CON_CODE_RENC'],
                                                    'fdm' : pool_event_fdm
                                                }
                                            )
                                            index_pool_event += 1

                                    #pool players
                                    #players_id_list = []
                                    for player in data_pool['players']:
                                        # create a new pool player
                                        if player['playerId'] != None :
                                            #players_id_list.append(player['playerId'])
                                            print("--- --- --- --- Updating player "+player['playerId']+" in pool "+str(pool['poolId']))
                                            
                                            club_obj, created = DClub.objects.update_or_create(
                                                id=player['clubId'],
                                                defaults = {
                                                    'name' : player['club'],
                                                    'region' : int(str(player['clubId'])[0:2]),
                                                    'departement' : int(str(player['clubId'])[2:4])
                                                }
                                            )
                                            
                                            player_obj, created = DPlayer.objects.update_or_create(
                                                id=player['playerId'],
                                                defaults = {
                                                    'club' : club_obj,
                                                    'first_name' : player['firstName'],
                                                    'last_name' : player['lastName'],
                                                    'gender' : 'M' if (player['playerId'][7:8] == '1') else 'F'
                                                }
                                            )
                                            
                                            pool_player_id = str(pool['poolId'])+"_"+player['playerId']
                                            DPoolPlayer.objects.update_or_create(
                                                id=pool_player_id,
                                                defaults = {
                                                    'player' : player_obj,
                                                    'pool': pool_obj,
                                                    'match_played' : player['statistics'][0][1],
                                                    'goal' : player['statistics'][1][1],
                                                    'saves' : player['statistics'][2][1],
                                                    'avg' : player['statistics'][3][1],
                                                    'avg_stop' : player['statistics'][4][1]
                                                }
                                            )
                                        else:
                                            print("Invalid palyer " + url_pool)

                                    #pool players      
                                    for pool_team in data_pool['teams']:
                                        # create a new pool team
                                        print("--- --- --- --- Updating team "+pool_team['name']+" in pool "+str(pool['poolId']))
                                        pool_team_id = str(pool['poolId'])+"_"+pool_team['name']
                                        
                                        DPoolTeam.objects.update_or_create(
                                            id=pool_team_id,
                                            defaults = {
                                                'pool' : pool_obj,
                                                'team_name' : pool_team['name'],
                                                'position' : pool_team['position'],
                                                'points' : pool_team['points'],
                                                'games' : pool_team['games'],
                                                'wins' : pool_team['wins'],
                                                'draws' : pool_team['draws'],
                                                'defeats' : pool_team['defeats'],
                                                'scored' : pool_team['scored'],
                                                'missed' : pool_team['missed'],
                                                'difference' : pool_team['difference']
                                            }
                                        )
                            #end download pool details 

                            #download pool players stats
                            url_pool_player_stat = base_url+"/player/"+str(pool['poolId'])
                            try:
                                response_pool_player_stat = requests.get(url_pool_player_stat)
                            except requests.exceptions.RequestException as e:
                                print("Error requesting pool player stat url " + url_pool_player_stat)
                            else:
                                #compute file hash
                                pool_player_hash = hashlib.md5(response_pool_player_stat.text.encode("utf-8")).hexdigest()
                            
                                #if players details has changed, parse and record file
                                if pool_obj.player_hash != pool_player_hash :
                                    # update pool
                                    print("--- --- --- New player hash: "+ pool_player_hash + ", old: " + pool_obj.player_hash )
                                    pool_obj.player_hash = pool_player_hash
                                    pool_obj.save()

                                    data_pool_player_stat = json.loads(response_pool_player_stat.text)

                                    data_pool_player_stat_keys = data_pool_player_stat.keys()
                                    for id in data_pool_player_stat_keys:
                                        try:
                                            player_obj = DPlayer.objects.get(pk=id)
                                        except DPlayer.DoesNotExist:
                                            print("Player does not exist " + id)
                                        else:
                                        
                                            game = 0
                                            for pool_game in data_pool_player_stat[id]['games']:
                                                # create a new pool player stat
                                                print("--- --- --- --- Updating player "+id+" stat in pool "+str(pool['poolId']))
                                                pool_player_stat_id = str(pool['poolId'])+"_"+id+"_"+str(game)
                                                
                                                #player_obj = DPlayer.objects.get(pk=id)

                                                DPoolPlayerStat.objects.update_or_create(
                                                    id=pool_player_stat_id,
                                                    defaults = {
                                                        'player' : player_obj,
                                                        'pool' : pool_obj,
                                                        'game' : game,
                                                        'goal' : pool_game['statistics'][0]['value'],
                                                        'saves' : pool_game['statistics'][1]['value'],
                                                        'mins' : pool_game['statistics'][2]['value'],
                                                        'warn' : pool_game['statistics'][3]['value'],
                                                        'dis' : pool_game['statistics'][4]['value']
                                                    }
                                                )
                                                
                                                game += 1
                            #end download pool players stats

    
    

class Command(BaseCommand):
    args = ''
    help = 'Update -Championnats départementaux- database'

    def handle(self, *args, **options):

        # scrap championnats departementaux
        scrap('D')
        # scrap championnats regionaux
        scrap('R')
        
    