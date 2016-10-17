import collections
import os

from peewee import *
from playhouse.postgres_ext import *

import utils


database_proxy = Proxy()

class BaseModel(Model):
    class Meta:
        database = database_proxy


class OverrideCandidate(BaseModel):
    nyt_candidate_description = TextField(null=True)
    nyt_candidate_name = CharField(null=True)
    nyt_races = ArrayField(field_class=CharField)
    nyt_candidate_important = BooleanField(null=True)
    nyt_winner = BooleanField(null=True)
    nyt_display_order = IntegerField(null=True)
    nyt_delegates = IntegerField(null=True)
    id = CharField(primary_key=True)

    class Meta:
        db_table = 'override_candidates'

    def serialize(self):
        return collections.OrderedDict([
            utils.make_field(self, 'nyt_candidate_name'),
            utils.make_field(self, 'nyt_candidate_important'),
            utils.make_field(self, 'nyt_candidate_description'),
            ('nyt_races', "{%s}" % ",".join([unicode(r) for r in self.nyt_races])),
            utils.make_field(self, 'nyt_display_order'),
            utils.make_field(self, 'nyt_winner'),
            utils.make_field(self, 'nyt_delegates'),
            utils.make_field(self, 'id')
        ])

    @classmethod
    def add_prez_candidates(cls):
        races = ElexRace.select().where(ElexRace.raceid == "0")
        for race in list(races):
            print "President: %s" % race.statepostal

            candidates = ElexResult.select()\
                            .where(ElexResult.statepostal == race.statepostal, ElexResult.raceid == race.raceid)\
                            .where(ElexResult.level << ['state', 'national'])

            candidates = sorted([e for e in candidates], key=lambda x: x.last)

            for idx, candidate in enumerate(candidates):
                try:
                    oc = cls.get(cls.id == candidate.candidate_unique_id)
                except cls.DoesNotExist:
                    oc = cls.create(id=candidate.candidate_unique_id)

                if not oc.nyt_races:
                    oc.nyt_races = []

                oc.nyt_races.append("%s-%s" % (race.statepostal,race.raceid))
                oc.nyt_display_order = idx
                oc.save()

    @classmethod
    def add_candidates(cls):
        races = ElexRace.select().where(ElexRace.raceid != "0")

        for race in list(races):
            print race.statepostal, race.officename, race.seatname

            candidates = list(race.state())
            for idx, candidate in enumerate(candidates):

                try:
                    oc = cls.get(cls.id == candidate.candidate_unique_id)
                except cls.DoesNotExist:
                    oc = cls.create(id=candidate.candidate_unique_id)

                oc.nyt_races = ["%s-%s" % (race.statepostal,race.raceid)]
                oc.nyt_display_order = idx
                oc.save()

        database_proxy.execute_sql(utils.ELEX_RESULTS_VIEW_COMMAND)
        database_proxy.execute_sql(utils.ELEX_CANDIDATE_VIEW_COMMAND)


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
    race_statepostal = CharField(null=True)
    nyt_called = BooleanField(null=True)
    nyt_race_important = BooleanField(null=True)

    class Meta:
        db_table = 'override_races'

    def serialize(self):
        return collections.OrderedDict([
            utils.make_field(self, 'nyt_race_preview'),
            utils.make_field(self, 'nyt_race_result_description'),
            utils.make_field(self, 'nyt_delegate_allocation'),
            utils.make_field(self, 'report'),
            utils.make_field(self, 'report_description'),
            utils.make_field(self, 'race_raceid'),
            utils.make_field(self, 'race_statepostal'),
            utils.make_field(self, 'nyt_race_name'),
            utils.make_field(self, 'nyt_race_description'),
            utils.make_field(self, 'accept_ap_calls'),
            utils.make_field(self, 'nyt_called'),
            utils.make_field(self, 'nyt_race_important')
        ])

    @classmethod
    def create_override_races(cls):
        races = ElexRace.select()
        for race in list(races):
            try:
                r = cls.get(cls.race_raceid == race.raceid, cls.race_statepostal == race.statepostal)
            except cls.DoesNotExist:
                r = cls.create(race_raceid=race.raceid, race_statepostal=race.statepostal)

        database_proxy.execute_sql(utils.ELEX_RESULTS_VIEW_COMMAND)
        database_proxy.execute_sql(utils.ELEX_CANDIDATE_VIEW_COMMAND)


class ElexCandidate(BaseModel):
    nyt_candidate_description = TextField(null=True)
    nyt_candidate_name = CharField(null=True)
    nyt_races = ArrayField(field_class=CharField)
    ballotorder = IntegerField(null=True)
    first = CharField(null=True)
    id = CharField(null=True)
    last = CharField(null=True)
    party = CharField(null=True)
    polid = CharField(null=True)
    polnum = CharField(null=True)
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
    race_statepostal = CharField(null=True)
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
        results = ElexResult.select()\
                            .where(ElexResult.statepostal == self.statepostal, ElexResult.raceid == self.raceid)\
                            .where(ElexResult.level == 'state')
        if len(results) == 0:
            results = ElexResult.select()\
                            .where(ElexResult.statepostal == self.statepostal, ElexResult.raceid == self.raceid)\
                            .where(ElexResult.level == None)
        return sorted([e for e in results], key=lambda x: x.last)

    def counties(self):
        results = ElexResult.select()\
                            .where(ElexResult.statepostal == self.statepostal, ElexResult.raceid == self.raceid)\
                            .where(ElexResult.level == 'county')
        return sorted([e for e in results], key=lambda x: x.last)

    def townships(self):
        results = ElexResult.select()\
                            .where(ElexResult.statepostal == self.statepostal, ElexResult.raceid == self.raceid)\
                            .where(ElexResult.level == 'county')
        return sorted([e for e in results], key=lambda x: x.last)

    def candidates(self):
        return None


class ElexResult(BaseModel):
    nyt_race_preview = TextField(null=True)
    nyt_race_result_description = TextField(null=True)
    nyt_delegate_allocation = TextField(null=True)
    report = BooleanField(null=True)
    report_description = TextField(null=True)
    nyt_candidate_description = TextField(null=True)
    nyt_candidate_name = CharField(null=True)
    accept_ap_calls = BooleanField(null=True)
    nyt_race_description = TextField(null=True)
    nyt_race_name = CharField(null=True)
    nyt_winner = BooleanField(null=True)
    race_raceid = CharField(null=True)
    race_statepostal = CharField(null=True)
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
    votecount = IntegerField(null=True)
    votepct = DecimalField(null=True)
    winner = BooleanField(null=True)
    nyt_race_important = BooleanField(null=True)
    nyt_candidate_important = BooleanField(null=True)
    nyt_called = BooleanField(null=True)
    nyt_display_order = IntegerField(null=True)
    nyt_delegates = IntegerField(null=True)
    candidate_unique_id = CharField(null=True)

    class Meta:
        db_table = "elex_results"

