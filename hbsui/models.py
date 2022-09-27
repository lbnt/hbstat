# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class DChampionship(models.Model):
    CATEGORY_CHOICES = [
       ('D', 'Départemental'),
       ('R', 'Régional'),
    ]
    id = models.CharField(primary_key=True, max_length=31)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=3)

    class Meta:
        managed = True
        db_table = 'd_championships'


class DCompetition(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    championship = models.ForeignKey(DChampionship, models.DO_NOTHING, db_column='championship')
    name = models.CharField(max_length=255)
    
    class Meta:
        managed = True
        db_table = 'd_competitions'


class DPool(models.Model):
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
    competition = models.ForeignKey(DCompetition, models.DO_NOTHING, db_column='competition')
    phase_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=31)
    age = models.CharField(max_length=2, choices=AGE_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    pool_hash = models.CharField(max_length=32, default="")
    player_hash = models.CharField(max_length=32, default="")

    class Meta:
        managed = True
        db_table = 'd_pools'


class DClub(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    name = models.CharField(max_length=255)
    region = models.IntegerField(blank=True, null=True)
    departement = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'd_clubs'


class DPlayer(models.Model):
    GENDER_CHOICES = [
       ('M', 'Masculins'),
       ('F', 'Féminines'),
    ]
    id = models.CharField(primary_key=True, max_length=31)
    club = models.ForeignKey(DClub, models.DO_NOTHING, db_column='club')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    class Meta:
        managed = True
        db_table = 'd_players'


class DPoolDate(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    pool = models.ForeignKey(DPool, models.DO_NOTHING, db_column='pool')
    start = models.DateField(blank=True, null=True)
    finish = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'd_pool_dates'


class DPoolEvent(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    pool = models.ForeignKey(DPool, models.DO_NOTHING, db_column='pool')
    date = models.ForeignKey(DPoolDate, models.DO_NOTHING, db_column='date')
    date_day = models.IntegerField(blank=True, null=True)
    date_date = models.DateField(blank=True, null=True)
    date_hour = models.IntegerField(blank=True, null=True)
    date_minute = models.IntegerField(blank=True, null=True)
    team_0_name = models.CharField(max_length=255)
    team_0_score = models.CharField(blank=True, null=True, max_length=2)
    team_1_name = models.CharField(max_length=255)
    team_1_score = models.CharField(blank=True, null=True, max_length=2)
    referee_0_name = models.CharField(blank=True, null=True, max_length=255)
    referee_1_name = models.CharField(blank=True, null=True, max_length=255)
    location_0 = models.CharField(blank=True, null=True, max_length=255)
    location_1 = models.CharField(blank=True, null=True, max_length=255)
    location_2 = models.CharField(blank=True, null=True, max_length=255)
    code = models.CharField(max_length=31)
    fdm = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'd_pool_events'


class DPoolPlayerStat(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    player = models.ForeignKey(DPlayer, models.DO_NOTHING, db_column='player')
    pool = models.ForeignKey(DPool, models.DO_NOTHING, db_column='pool')
    game = models.IntegerField(blank=True, null=True)
    goal = models.IntegerField(blank=True, null=True)
    saves = models.IntegerField(blank=True, null=True)
    mins = models.IntegerField(blank=True, null=True)
    warn = models.IntegerField(blank=True, null=True)
    dis = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'd_pool_player_stats'


class DPoolPlayer(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    player = models.ForeignKey(DPlayer, models.DO_NOTHING, db_column='player')
    pool = models.ForeignKey(DPool, models.DO_NOTHING, db_column='pool')
    match_played = models.IntegerField(blank=True, null=True)
    goal = models.IntegerField(blank=True, null=True)
    saves = models.IntegerField(blank=True, null=True)
    avg = models.FloatField(blank=True, null=True)
    avg_stop = models.FloatField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'd_pool_players'


class DPoolTeam(models.Model):
    id = models.CharField(primary_key=True, max_length=31)
    pool = models.ForeignKey(DPool, models.DO_NOTHING, db_column='pool')
    team_name = models.CharField(max_length=255)
    position = models.IntegerField(blank=True, null=True)
    points = models.IntegerField(blank=True, null=True)
    games = models.IntegerField(blank=True, null=True)
    wins = models.IntegerField(blank=True, null=True)
    draws = models.IntegerField(blank=True, null=True)
    defeats = models.IntegerField(blank=True, null=True)
    scored = models.IntegerField(blank=True, null=True)
    missed = models.IntegerField(blank=True, null=True)
    difference = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'd_pool_teams'
