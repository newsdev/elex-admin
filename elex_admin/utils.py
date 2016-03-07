import glob
import os

CDN_URL = os.environ.get('ELEX_ADMIN_CDN_URL', 'http://int.nyt.com.s3.amazonaws.com/cdn')

ELEX_RACE_VIEW_COMMAND = """CREATE OR REPLACE VIEW elex_races as
   SELECT o.*, r.* from races as r
   LEFT JOIN override_races as o on r.raceid = o.race_raceid
;"""

ELEX_CANDIDATE_VIEW_COMMAND = """CREATE OR REPLACE VIEW elex_candidates as
   SELECT c.*, r.* from candidates as r
       LEFT JOIN override_candidates as c on r.candidateid = c.candidate_candidateid
;"""

ELEX_RESULTS_VIEW_COMMAND = """CREATE OR REPLACE VIEW elex_results as
   SELECT n.delegates_count as us_delegates_count,
       n.superdelegates_count as us_superdelegates_count,
       d.delegates_count,
       d.superdelegates_count,
       o.*,
       c.*,
       r.*
       FROM results as r
           LEFT JOIN override_candidates as c on r.candidateid = c.candidate_candidateid
           LEFT JOIN override_races as o on r.raceid = o.race_raceid
           LEFT JOIN delegates as d on r.statepostal = d.state AND r.polid = d.candidateid
           LEFT JOIN delegates as n on r.polid = n.candidateid AND n.state = 'US'
;"""

def make_field(cls, field_name):
    return (field_name, getattr(cls, field_name))

def update_views(database):
    """
    Resets the Postgres VIEWs.
    """
    database.execute_sql(ELEX_RESULTS_VIEW_COMMAND)
    database.execute_sql(ELEX_RACE_VIEW_COMMAND)
    database.execute_sql(ELEX_CANDIDATE_VIEW_COMMAND)

def clean_payload(payload):
    """
    Serializes payload from form strings to more useful Python things.
    """
    for k,v in payload.items():
        v = v[0]
        if v == u'':
            v = None
        if v == 'true':
            v = True
        if v == 'false':
            v = False
        payload[k] = v
    return payload

def update_model(cls, payload):
    """
    Given a model class and a set of keys/values, will
    update and save that model class with the keys/values.
    """
    for k,v in payload.items():
        if k != 'nyt_winner':
            setattr(cls,k,v)
    cls.save()

def set_winner(candidateid, raceid):
    """
    Handles setting a winner. Sets a race to called and
    a candidate as the winner and other candidates as
    not winners. If the candidateid is null, will reset 
    the race to be uncalled and remove the previous winner.
    """
    import models
    if candidateid:
        r = models.OverrideRace.update(nyt_called=True).where(models.OverrideRace.race_raceid == int(raceid))
        nc = models.OverrideCandidate\
                .update(nyt_winner=False)\
                .where(
                    models.OverrideCandidate.candidate_candidateid != int(candidateid),
                    models.OverrideCandidate.nyt_races.contains(int(raceid))
                )
        yc = models.OverrideCandidate\
                .update(nyt_winner=True)\
                .where(
                    models.OverrideCandidate.candidate_candidateid == int(candidateid),
                    models.OverrideCandidate.nyt_races.contains(int(raceid))
                )

        r.execute()
        nc.execute()
        yc.execute()
    else:
        r = models.OverrideRace.update(nyt_called=False).where(models.OverrideRace.race_raceid == int(raceid))
        nc = models.OverrideCandidate\
                .update(nyt_winner=False)\
                .where(models.OverrideCandidate.nyt_races.contains(int(raceid)))
        r.execute()
        nc.execute()

def build_context(racedate):
    """
    Every page needs these two things.
    """
    context = {}
    context['CDN_URL'] = CDN_URL
    context['RACEDATE'] = racedate
    context['race_dates'] = sorted([d.split('/')[-1].split('.ini')[0] for d in glob.glob('elex_admin/*.ini')], key=lambda x:x)
    return dict(context)
