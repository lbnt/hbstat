# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


### v2
class Championship(models.Model):
    CATEGORY_CHOICES = [
       ('DEP', 'Départemental'),
       ('REG', 'Régional'),
       ('NAT', 'National'),
       ('CDF', 'Coupe de France'),
       ('I-C', 'Inter comités'),
       ('I-L', 'inter ligues'),
    ]
    DEPARTEMENT_CHOICES = [
       ('01', 'Ain'),
       ('02', 'Aisne'),
       ('03', 'Allier'),
       ('04', 'Alpes de Haute-Provence'),
       ('05', 'Hautes-Alpes'),
       ('06', 'Alpes-Maritimes'),
       ('07', 'Ardêche'),
       ('08', 'Ardennes'),
       ('09', 'Ariège'),
       ('10', 'Aube'),
       ('11', 'Aude'),
       ('12', 'Aveyron'),
       ('13', 'Bouches-du-Rhône'),
       ('14', 'Calvados'),
       ('15', 'Cantal'),
       ('17', 'Charente'),
       ('17', 'Charente-Maritime'),
       ('18', 'Cher'),
       ('19', 'Corrèze'),
       ('2A', 'Corse-du-Sud'),
       ('2B', 'Haute-Corse'),
       ('21', 'Côte-d Or'),
       ('22', 'Côtes d Armor'),
       ('23', 'Creuse'),
       ('24', 'Dordogne'),
       ('25', 'Doubs'),
       ('26', 'Drôme'),
       ('27', 'Eure'),
       ('28', 'Eure-et-Loir'),
       ('29', 'Finistère'),
       ('30', 'Gard'),
       ('31', 'Haute-Garonne'),
       ('32', 'Gers'),
       ('33', 'Gironde'),
       ('34', 'Hérault'),
       ('35', 'Île-et-Vilaine'),
       ('36', 'Indre'),
       ('37', 'Indre-et-Loire'),
       ('38', 'Isère'),
       ('39', 'Jura'),
       ('40', 'Landes'),
       ('41', 'Loir-et-Cher'),
       ('42', 'Loire'),
       ('43', 'Haute-Loire'),
       ('44', 'Loire-Atlantique'),
       ('45', 'Loiret'),
       ('46', 'Lot'),
       ('47', 'Lot-et-Garonne'),
       ('48', 'Lozère'),
       ('49', 'Maine-et-Loire'),
       ('50', 'Manche'),
       ('51', 'Marne'),
       ('52', 'Haute-Marne'),
       ('53', 'Mayenne'),
       ('54', 'Meurthe-et-Moselle'),
       ('55', 'Meuse'),
       ('56', 'Morbihan'),
       ('57', 'Moselle'),
       ('58', 'Nièvre'),
       ('59', 'Nord'),
       ('60', 'Oise'),
       ('61', 'Orne'),
       ('62', 'Pas-de-Calais'),
       ('63', 'Puy-de-Dôme'),
       ('64', 'Pyrénées-Atlantiques'),
       ('65', 'Hautes-Pyrénées'),
       ('66', 'Pyrénées-Orientales'),
       ('67', 'Bas-Rhin'),
       ('68', 'Haut-Rhin'),
       ('69', 'Rhône'),
       ('70', 'Haute-Saône'),
       ('71', 'Saône-et-Loire'),
       ('72', 'Sarthe'),
       ('73', 'Savoie'),
       ('74', 'Haute-Savoie'),
       ('75', 'Paris'),
       ('76', 'Seine-Maritime'),
       ('77', 'Seine-et-Marne'),
       ('78', 'Yvelines'),
       ('79', 'Deux-Sèvres'),
       ('80', 'Somme'),
       ('81', 'Tarn'),
       ('82', 'Tarn-et-Garonne'),
       ('83', 'Var'),
       ('84', 'Vaucluse'),
       ('85', 'Vendée'),
       ('86', 'Vienne'),
       ('87', 'Haute-Vienne'),
       ('88', 'Vosges'),
       ('89', 'Yonne'),
       ('90', 'Territoire-de-Belfort'),
       ('91', 'Essonne'),
       ('92', 'Hauts-de-Seine'),
       ('93', 'Seine-Saint-Denis'),
       ('94', 'Val-de-Marne'),
       ('95', 'Val-d Oise'),       
    ]
    REGION_CHOICES = [
       ('51', 'Auvergne-Rhône-Alpes'),
       ('52', 'Bourgogne-Franche-Comté'),
       ('53', 'Bretagne'),
       ('54', 'Centre-Val de Loire'),
       ('55', 'Corse'),
       ('56', 'Grand Est'),
       ('57', 'Hauts-de-France'),
       ('58', 'Ile-de-France'),
       ('59', 'Normandie'),
       ('60', 'Nouvelle-Aquitaine'),
       ('61', 'Occitanie'),
       ('62', 'Pays de la Loire'),
       ('63', 'Provence-Alpes-Côte d’Azur'),       
    ]
    
    id = models.CharField(primary_key=True, max_length=31)
    season= models.CharField(max_length=3)
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=255)
    acronym = models.CharField(max_length=31)
    type = models.CharField(max_length=31)
    code = models.CharField(max_length=31)
    departement = models.CharField(max_length=2, choices=DEPARTEMENT_CHOICES)
    region = models.CharField(max_length=2, choices=REGION_CHOICES)
    logo = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'championships'

class Competition(models.Model):
    GENDER_CHOICES = [
       ('Z', 'Mixte'),
       ('M', 'Masculins'),
       ('F', 'Féminines'),
    ]
    AGE_CHOICES = [
       ('00', 'Senior'),
       ('01', 'Senior'),
       ('02', 'Senior'),
       ('10', 'Senior'),
       ('35', '-18'),
       ('40', '-17'),
       ('45', '-16'),
       ('50', '-15'),
       ('55', '-14'),
       ('60', '-13'),
       ('65', '-12'),
       ('70', '-11'),
       ('75', '-10'),
       ('80', '-9'),
       ('85', 'Mini-Hand'),
    ]
    id = models.CharField(primary_key=True, max_length=31)
    championship = models.ForeignKey(Championship, models.DO_NOTHING, db_column='championship')
    name = models.CharField(max_length=255)
    age = models.CharField(max_length=2, choices=AGE_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    logo = models.CharField(max_length=255, null=True)
    last_update = models.DateTimeField()

    
    class Meta:
        managed = True
        db_table = 'competitions'

class Phase(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    competition = models.ForeignKey(Competition, models.DO_NOTHING, db_column='competition')
    name = models.CharField(max_length=255)
    last_update = models.DateTimeField()
    
    class Meta:
        managed = True
        db_table = 'phases'

class Pool(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    phase = models.ForeignKey(Phase, models.DO_NOTHING, db_column='phase')
    name = models.CharField(max_length=255)
    last_update = models.DateTimeField()
    
    class Meta:
        managed = True
        db_table = 'pools'

class Club(models.Model):
    #TODO ne pas repeter ces choices
    DEPARTEMENT_CHOICES = [
       ('01', 'Ain'),
       ('02', 'Aisne'),
       ('03', 'Allier'),
       ('04', 'Alpes de Haute-Provence'),
       ('05', 'Hautes-Alpes'),
       ('06', 'Alpes-Maritimes'),
       ('07', 'Ardêche'),
       ('08', 'Ardennes'),
       ('09', 'Ariège'),
       ('10', 'Aube'),
       ('11', 'Aude'),
       ('12', 'Aveyron'),
       ('13', 'Bouches-du-Rhône'),
       ('14', 'Calvados'),
       ('15', 'Cantal'),
       ('17', 'Charente'),
       ('17', 'Charente-Maritime'),
       ('18', 'Cher'),
       ('19', 'Corrèze'),
       ('2A', 'Corse-du-Sud'),
       ('2B', 'Haute-Corse'),
       ('21', 'Côte-d Or'),
       ('22', 'Côtes d Armor'),
       ('23', 'Creuse'),
       ('24', 'Dordogne'),
       ('25', 'Doubs'),
       ('26', 'Drôme'),
       ('27', 'Eure'),
       ('28', 'Eure-et-Loir'),
       ('29', 'Finistère'),
       ('30', 'Gard'),
       ('31', 'Haute-Garonne'),
       ('32', 'Gers'),
       ('33', 'Gironde'),
       ('34', 'Hérault'),
       ('35', 'Île-et-Vilaine'),
       ('36', 'Indre'),
       ('37', 'Indre-et-Loire'),
       ('38', 'Isère'),
       ('39', 'Jura'),
       ('40', 'Landes'),
       ('41', 'Loir-et-Cher'),
       ('42', 'Loire'),
       ('43', 'Haute-Loire'),
       ('44', 'Loire-Atlantique'),
       ('45', 'Loiret'),
       ('46', 'Lot'),
       ('47', 'Lot-et-Garonne'),
       ('48', 'Lozère'),
       ('49', 'Maine-et-Loire'),
       ('50', 'Manche'),
       ('51', 'Marne'),
       ('52', 'Haute-Marne'),
       ('53', 'Mayenne'),
       ('54', 'Meurthe-et-Moselle'),
       ('55', 'Meuse'),
       ('56', 'Morbihan'),
       ('57', 'Moselle'),
       ('58', 'Nièvre'),
       ('59', 'Nord'),
       ('60', 'Oise'),
       ('61', 'Orne'),
       ('62', 'Pas-de-Calais'),
       ('63', 'Puy-de-Dôme'),
       ('64', 'Pyrénées-Atlantiques'),
       ('65', 'Hautes-Pyrénées'),
       ('66', 'Pyrénées-Orientales'),
       ('67', 'Bas-Rhin'),
       ('68', 'Haut-Rhin'),
       ('69', 'Rhône'),
       ('70', 'Haute-Saône'),
       ('71', 'Saône-et-Loire'),
       ('72', 'Sarthe'),
       ('73', 'Savoie'),
       ('74', 'Haute-Savoie'),
       ('75', 'Paris'),
       ('76', 'Seine-Maritime'),
       ('77', 'Seine-et-Marne'),
       ('78', 'Yvelines'),
       ('79', 'Deux-Sèvres'),
       ('80', 'Somme'),
       ('81', 'Tarn'),
       ('82', 'Tarn-et-Garonne'),
       ('83', 'Var'),
       ('84', 'Vaucluse'),
       ('85', 'Vendée'),
       ('86', 'Vienne'),
       ('87', 'Haute-Vienne'),
       ('88', 'Vosges'),
       ('89', 'Yonne'),
       ('90', 'Territoire-de-Belfort'),
       ('91', 'Essonne'),
       ('92', 'Hauts-de-Seine'),
       ('93', 'Seine-Saint-Denis'),
       ('94', 'Val-de-Marne'),
       ('95', 'Val-d Oise'),       
    ]
    REGION_CHOICES = [
       ('51', 'Auvergne-Rhône-Alpes'),
       ('52', 'Bourgogne-Franche-Comté'),
       ('53', 'Bretagne'),
       ('54', 'Centre-Val de Loire'),
       ('55', 'Corse'),
       ('56', 'Grand Est'),
       ('57', 'Hauts-de-France'),
       ('58', 'Ile-de-France'),
       ('59', 'Normandie'),
       ('60', 'Nouvelle-Aquitaine'),
       ('61', 'Occitanie'),
       ('62', 'Pays de la Loire'),
       ('63', 'Provence-Alpes-Côte d’Azur'),       
    ]
    id = models.CharField(primary_key=True, max_length=31)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=32, blank=True, null=True)
    departement = models.CharField(max_length=2, choices=DEPARTEMENT_CHOICES, blank=True, null=True)
    region = models.CharField(max_length=2, choices=REGION_CHOICES, blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'clubs'

class Player(models.Model):
    GENDER_CHOICES = [
       ('M', 'Masculins'),
       ('F', 'Féminines'),
    ]
    id = models.CharField(primary_key=True, max_length=31)
    club = models.ForeignKey(Club, models.DO_NOTHING, db_column='club')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    match_played = models.IntegerField(blank=True, null=True)
    goals = models.IntegerField(blank=True, null=True)
    penaltythrows = models.IntegerField(blank=True, null=True)
    shots = models.IntegerField(blank=True, null=True)
    saves = models.IntegerField(blank=True, null=True)
    mins = models.IntegerField(blank=True, null=True)
    warn = models.IntegerField(blank=True, null=True)
    dis = models.IntegerField(blank=True, null=True)
    avg_goals = models.FloatField(blank=True, null=True)
    avg_saves = models.FloatField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'players'

class Gym(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    location = models.CharField(blank=True, null=True, max_length=511)
    
    class Meta:
        managed = True
        db_table = 'gyms'

class PoolDay(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    pool = models.ForeignKey(Pool, models.DO_NOTHING, db_column='pool')
    index = models.IntegerField(blank=True, null=True)
    start = models.DateField(blank=True, null=True)
    finish = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'pool_days'

class PoolTeam(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    pool = models.ForeignKey(Pool, models.DO_NOTHING, db_column='pool')
    club = models.ForeignKey(Club, models.DO_NOTHING, db_column='club')
    name = models.CharField(max_length=255)
    ranking = models.IntegerField(blank=True, null=True)
    points = models.IntegerField(blank=True, null=True)
    games = models.IntegerField(blank=True, null=True)
    wins = models.IntegerField(blank=True, null=True)
    draws = models.IntegerField(blank=True, null=True)
    defeats = models.IntegerField(blank=True, null=True)
    scored = models.IntegerField(blank=True, null=True)
    missed = models.IntegerField(blank=True, null=True)
    difference = models.IntegerField(blank=True, null=True)
    last_results = models.CharField(max_length=31, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'pool_teams'

class PoolMatch(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    pool = models.ForeignKey(Pool, models.DO_NOTHING, db_column='pool')
    day = models.ForeignKey(PoolDay, models.DO_NOTHING, db_column='day')
    date = models.DateTimeField(blank=True, null=True)
    played = models.BooleanField(blank=True, null=True)
    team_1 = models.ForeignKey(PoolTeam, models.DO_NOTHING, db_column='team1', related_name='team1')
    team_1_score = models.CharField(blank=True, null=True, max_length=2)
    team_1_score_ht = models.CharField(blank=True, null=True, max_length=2)
    team_1_officials = models.JSONField(null=True)
    team_2 = models.ForeignKey(PoolTeam, models.DO_NOTHING, db_column='team2', related_name='team2')
    team_2_score = models.CharField(blank=True, null=True, max_length=2)
    team_2_score_ht = models.CharField(blank=True, null=True, max_length=2)
    team_2_officials = models.JSONField(null=True)
    fdm = models.CharField(max_length=31)
    officials = models.JSONField(null=True)
    gym = models.ForeignKey(Gym, models.DO_NOTHING, db_column='gym', null=True)
    timeline = models.JSONField(null=True)

    class Meta:
        managed = True
        db_table = 'pool_matchs'

class PlayerMatchStat(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    player = models.ForeignKey(Player, models.DO_NOTHING, db_column='player')
    pool = models.ForeignKey(Pool, models.DO_NOTHING, db_column='pool')
    match = models.ForeignKey(PoolMatch, models.DO_NOTHING, db_column='match')
    goals = models.IntegerField(blank=True, null=True)
    penaltythrows = models.IntegerField(blank=True, null=True)
    shots = models.IntegerField(blank=True, null=True)
    saves = models.IntegerField(blank=True, null=True)
    mins = models.IntegerField(blank=True, null=True)
    warn = models.IntegerField(blank=True, null=True)
    dis = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'player_match_stats'

class PlayerPoolStat(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    player = models.ForeignKey(Player, models.DO_NOTHING, db_column='player')
    pool = models.ForeignKey(Pool, models.DO_NOTHING, db_column='pool')
    match_played = models.IntegerField(blank=True, null=True)
    goals = models.IntegerField(blank=True, null=True)
    penaltythrows = models.IntegerField(blank=True, null=True)
    shots = models.IntegerField(blank=True, null=True)
    saves = models.IntegerField(blank=True, null=True)
    mins = models.IntegerField(blank=True, null=True)
    warn = models.IntegerField(blank=True, null=True)
    dis = models.IntegerField(blank=True, null=True)
    avg_goals = models.FloatField(blank=True, null=True)
    avg_saves = models.FloatField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'player_pool_stats'

