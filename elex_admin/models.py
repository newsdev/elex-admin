import os

from peewee import *
from playhouse.postgres_ext import *

import utils

database = PostgresqlExtDatabase('elex_%s' % os.environ.get('RACEDATE', None),
            user=os.environ.get('ELEX_ADMIN_USER', 'elex'),
            host=os.environ.get('ELEX_ADMIN_HOST', '127.0.0.1')
)


class BaseModel(Model):
    class Meta:
        database = database


class OverrideCandidate(BaseModel):
    candidate_candidateid = CharField(db_column='candidate_candidateid', primary_key=True)
    nyt_candidate_description = TextField(null=True)
    nyt_candidate_name = CharField(null=True)
    nyt_races = ArrayField(field_class=IntegerField)
    nyt_candidate_important = BooleanField(null=True)
    nyt_winner = BooleanField(null=True)
    nyt_display_order = IntegerField(null=True)
    nyt_delegates = IntegerField(null=True)

    class Meta:
        db_table = 'override_candidates'

    @classmethod
    def add_candidates(cls):
        races = ElexRace.select()
        for race in list(races):
            candidates = list(race.state())
            for idx, candidate in enumerate(candidates):
                try:
                    oc = cls.get(cls.candidate_candidateid == candidate.candidateid)
                except cls.DoesNotExist:
                    oc = cls.create(candidate_candidateid=candidate.candidateid)
                oc.nyt_races = [int(race.raceid)]
                oc.nyt_display_order = idx
                oc.save()
                print oc.candidate_candidateid

        database.execute_sql(utils.ELEX_RESULTS_VIEW_COMMAND)
        database.execute_sql(utils.ELEX_CANDIDATE_VIEW_COMMAND)


class OverrideRace(BaseModel):
    nyt_race_preview = TextField(null=True)
    nyt_race_result_description = TextField(null=True)
    nyt_delegate_allocation = TextField(null=True)
    report = BooleanField(null=True)
    report_description = TextField(null=True)
    accept_ap_calls = BooleanField(null=True)
    nyt_race_description = TextField(null=True)
    nyt_race_name = CharField(null=True)
    race_raceid = CharField(primary_key=True)
    nyt_race_important = BooleanField(null=True)
    nyt_called = BooleanField(null=True)

    class Meta:
        db_table = 'override_races'

    @classmethod
    def create_override_races(cls):
        races = ElexRace.select()
        for race in list(races):
            print race.raceid
            try:
                r = cls.get(cls.race_raceid == race.raceid)
            except cls.DoesNotExist:
                r = cls.create(race_raceid=race.raceid)

        database.execute_sql(utils.ELEX_RESULTS_VIEW_COMMAND)
        database.execute_sql(utils.ELEX_CANDIDATE_VIEW_COMMAND)


class ElexCandidate(BaseModel):
    candidate_candidateid = CharField(db_column='candidate_candidateid', primary_key=True)
    nyt_candidate_description = TextField(null=True)
    nyt_candidate_name = CharField(null=True)
    nyt_races = ArrayField(field_class=IntegerField)
    ballotorder = IntegerField(null=True)
    candidateid = CharField(null=True)
    first = CharField(null=True)
    id = CharField(null=True)
    last = CharField(null=True)
    party = CharField(null=True)
    polid = CharField(null=True)
    polnum = CharField(null=True)
    unique = CharField(db_column='unique_id', null=True)
    nyt_candidate_important = BooleanField(null=True)
    nyt_winner = BooleanField(null=True)
    nyt_display_order = IntegerField(null=True)
    nyt_delegates = IntegerField(null=True)

    class Meta:
        db_table = 'elex_candidates'

    def __unicode__(self):
        if self.nyt_candidate_name:
            return self.nyt_candidate_name
        return "%s %s" % (self.first, self.last)


class ElexRace(BaseModel):
    nyt_race_preview = TextField(null=True)
    nyt_race_result_description = TextField(null=True)
    nyt_delegate_allocation = TextField(null=True)
    report = BooleanField(null=True)
    report_description = TextField(null=True)
    accept_ap_calls = BooleanField(null=True)
    nyt_race_description = TextField(null=True)
    nyt_race_name = CharField(null=True)
    race_raceid = CharField(primary_key=True)
    description = CharField(null=True)
    id = CharField(null=True)
    initialization_data = BooleanField(null=True)
    lastupdated = DateField(null=True)
    national = BooleanField(null=True)
    officeid = CharField(null=True)
    officename = CharField(null=True)
    party = CharField(null=True)
    raceid = CharField(null=True)
    racetype = CharField(null=True)
    racetypeid = CharField(null=True)
    seatname = CharField(null=True)
    seatnum = CharField(null=True)
    statename = CharField(null=True)
    statepostal = CharField(null=True)
    test = BooleanField(null=True)
    uncontested = BooleanField(null=True)
    nyt_race_important = BooleanField(null=True)
    nyt_called = BooleanField(null=True)

    class Meta:
        db_table = 'elex_races'

    def __unicode__(self):
        return "%s %s %s %s" % (self.statepostal, self.party, self.officename, self.racetype)

    def state(self):
        results = ElexResult.select().where(ElexResult.raceid == self.raceid).where(ElexResult.level == 'state')
        return sorted([e for e in results], key=lambda x: x.last)

    def counties(self):
        results = ElexResult.select().where(ElexResult.raceid == self.raceid).where(ElexResult.level == 'county')
        return sorted([e for e in results], key=lambda x: x.last)

    def townships(self):
        results = ElexResult.select().where(ElexResult.raceid == self.raceid).where(ElexResult.level == 'county')
        return sorted([e for e in results], key=lambda x: x.last)

    def candidates(self):
        return None


class ElexResult(BaseModel):
    nyt_race_preview = TextField(null=True)
    nyt_race_result_description = TextField(null=True)
    nyt_delegate_allocation = TextField(null=True)
    report = BooleanField(null=True)
    report_description = TextField(null=True)
    candidate_candidateid = CharField(db_column='candidate_candidateid')
    nyt_candidate_description = TextField(null=True)
    nyt_candidate_name = CharField(null=True)
    accept_ap_calls = BooleanField(null=True)
    nyt_race_description = TextField(null=True)
    nyt_race_name = CharField(null=True)
    nyt_winner = BooleanField(null=True)
    race_raceid = CharField(null=True)
    ballotorder = IntegerField(null=True)
    candidateid = CharField(null=True)
    description = CharField(null=True)
    fipscode = CharField(null=True)
    first = CharField(null=True)
    id = CharField(null=True)
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
    unique = CharField(db_column='unique_id', null=True, primary_key=True)
    votecount = IntegerField(null=True)
    votepct = DecimalField(null=True)
    winner = BooleanField(null=True)
    nyt_race_important = BooleanField(null=True)
    nyt_candidate_important = BooleanField(null=True)
    nyt_called = BooleanField(null=True)
    nyt_display_order = IntegerField(null=True)
    nyt_delegates = IntegerField(null=True)

    class Meta:
        db_table = "elex_results"

