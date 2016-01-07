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
   SELECT o.*, c.*, r.* from results as r
       LEFT JOIN override_candidates as c on r.candidateid = c.candidate_candidateid
       LEFT JOIN override_races as o on r.raceid = o.race_raceid
;"""

RACEDATE = os.environ.get('RACEDATE', None)

def update_views(database):
    """
    Resets the Postgres VIEWs.
    """
    database.execute_sql(utils.ELEX_RESULTS_VIEW_COMMAND)
    database.execute_sql(utils.ELEX_RACE_VIEW_COMMAND)
    database.execute_sql(utils.ELEX_CANDIDATE_VIEW_COMMAND)

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
        setattr(cls,k,v)
    cls.save()

def set_winner(candidateid, raceid):
    """
    This is the part where I might need to do more things?
    Will check in with Wilson.
    """
    print candidateid, raceid

def build_context():
    """
    Every page needs these two things.
    """
    context = {}
    context['CDN_URL'] = CDN_URL
    context['RACEDATE'] = RACEDATE
    return dict(context)
