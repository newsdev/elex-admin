import collections
import os

from peewee import *
from playhouse.postgres_ext import *

import general.utils as utils


database_proxy = Proxy()

class BaseModel(Model):
    class Meta:
        database = database_proxy


class OverrideCandidate(BaseModel):
    candidate_unique_id = CharField(db_column='candidate_unique_id', null=True, primary_key=True)
    nyt_name = CharField(null=True)
    nyt_winner = BooleanField(null=True)
    nyt_electwon = IntegerField(null=True)

    raceid = CharField(null=True)
    statepostal = CharField(null=True)

    class Meta:
        db_table = 'override_candidates'


class OverrideRace(BaseModel):
    accept_ap_calls = BooleanField(null=True)
    nyt_called = BooleanField(null=True)
    nyt_race_description = CharField(null=True)
    nyt_race_name = CharField(null=True)
    race_unique_id = TextField(db_column='race_unique_id', null=True, primary_key=True)
    report = BooleanField(null=True)

    raceid = CharField(null=True)
    statepostal = CharField(null=True)

    class Meta:
        db_table = 'override_races'

class ElexRace(BaseModel):
    accept_ap_calls = BooleanField(null=True)
    raceid = CharField(null=True)
    statepostal = CharField(null=True)
    officeid = CharField(null=True)
    national = BooleanField(null=True)
    race_unique_id = TextField(db_column='race_unique_id', null=True, primary_key=True)

    class Meta:
        db_table = 'elex_races'


class ElexResult(BaseModel):
    nyt_name = CharField(null=True)
    nyt_winner = BooleanField(null=True)
    nyt_electwon = IntegerField(null=True)

    accept_ap_calls = BooleanField(null=True)
    nyt_called = BooleanField(null=True)
    nyt_race_description = CharField(null=True)
    nyt_race_name = CharField(null=True)
    race_unique_id = TextField(db_column='race_unique_id', null=True)
    report = BooleanField(null=True)

    ballotorder = IntegerField(null=True)
    candidate_unique_id = CharField(db_column='candidate_unique_id', null=True)
    candidateid = CharField(null=True)
    delegatecount = IntegerField(null=True)
    description = CharField(null=True)
    electiondate = CharField(null=True)
    electtotal = IntegerField(null=True)
    electwon = IntegerField(null=True)
    fipscode = CharField(null=True)
    first = CharField(null=True)
    id = CharField(null=True, primary_key=True)
    incumbent = BooleanField(null=True)
    initialization_data = BooleanField(null=True)
    is_ballot_position = BooleanField(null=True)
    last = CharField(null=True)
    lastupdated = CharField(null=True)
    level = CharField(null=True)
    national = BooleanField(null=True)
    officeid = CharField(null=True)
    officename = CharField(null=True)
    party = CharField(null=True)
    polid = CharField(null=True)
    polnum = CharField(null=True)
    precinctsreporting = IntegerField(null=True)
    precinctsreportingpct = DecimalField(null=True)
    precinctstotal = IntegerField(null=True)
    raceid = CharField(null=True)
    racetype = CharField(null=True)
    racetypeid = CharField(null=True)
    reportingunitid = CharField(null=True)
    reportingunitname = CharField(null=True)
    runoff = BooleanField(null=True)
    seatname = CharField(null=True)
    seatnum = CharField(null=True)
    statename = CharField(null=True)
    statepostal = CharField(null=True)
    test = BooleanField(null=True)
    uncontested = BooleanField(null=True)
    votecount = IntegerField(null=True)
    votepct = DecimalField(null=True)
    winner = BooleanField(null=True)

    class Meta:
        db_table = 'elex_results'
