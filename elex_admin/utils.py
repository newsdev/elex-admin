import glob
import os

CDN_URL = os.environ.get('ELEX_ADMIN_CDN_URL', 'http://int.nyt.com.s3.amazonaws.com/cdn')

ELEX_RACE_VIEW_COMMAND = """CREATE OR REPLACE VIEW elex_races as
   SELECT o.*, r.* from races as r
   LEFT JOIN override_races as o on r.raceid = o.race_raceid and r.statepostal = o.race_statepostal
;"""

ELEX_CANDIDATE_VIEW_COMMAND = """CREATE OR REPLACE VIEW elex_candidates as
   SELECT c.*, r.* from candidates as r
       LEFT JOIN override_candidates as c on r.candidateid = c.candidate_candidateid
;"""

ELEX_RESULTS_VIEW_COMMAND = """CREATE OR REPLACE VIEW elex_results as
       (SELECT x.*, y.*, z.* FROM local_results as z
                LEFT JOIN override_candidates as y on z.candidateid = y.candidate_candidateid
                LEFT JOIN override_races as x on z.raceid = x.race_raceid and z.statepostal = x.race_statepostal)
        UNION ALL
        (SELECT a.*, b.*, c.* FROM national_results as c
                LEFT JOIN override_candidates as b on c.candidateid = b.candidate_candidateid
                LEFT JOIN override_races as a on c.raceid = a.race_raceid and c.statepostal = a.race_statepostal)"""

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
        r = models.OverrideRace.update(nyt_called=True).where(
            models.OverrideRace.race_raceid == raceid.split('-')[1],
            models.OverrideRace.race_statepostal == raceid.split('-')[0]
        )
        nc = models.OverrideCandidate\
                .update(nyt_winner=False)\
                .where(
                    models.OverrideCandidate.candidate_candidateid != int(candidateid),
                    models.OverrideCandidate.nyt_races.contains(raceid)
                )
        yc = models.OverrideCandidate\
                .update(nyt_winner=True)\
                .where(
                    models.OverrideCandidate.candidate_candidateid == int(candidateid),
                    models.OverrideCandidate.nyt_races.contains(raceid)
                )

        r.execute()
        nc.execute()
        yc.execute()
    else:
        r = models.OverrideRace.update(nyt_called=False).where(
            models.OverrideRace.race_raceid == raceid.split('-')[1],
            models.OverrideRace.race_statepostal == raceid.split('-')[0]
        )
        nc = models.OverrideCandidate\
                .update(nyt_winner=False)\
                .where(models.OverrideCandidate.nyt_races.contains(raceid))
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
    context['timeout'] = os.environ.get('ELEX_LOADER_TIMEOUT', '30')
    if os.path.isfile('/tmp/elex_loader_timeout.sh'):
        with open('/tmp/elex_loader_timeout.sh') as readfile:
            context['timeout'] = readfile.read().split('=')[1].strip()
    return dict(context)
