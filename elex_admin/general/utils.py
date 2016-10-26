import glob
import os

CDN_URL = os.environ.get('ELEX_ADMIN_CDN_URL', 'http://int.nyt.com.s3.amazonaws.com/cdn')

ELEX_RACE_VIEW_COMMAND = """
CREATE OR REPLACE VIEW elex_races AS
    SELECT r.raceid, r.statepostal, r.officeid, r.national, o.race_unique_id, o.accept_ap_calls
        FROM results AS r
            LEFT JOIN override_races AS o ON o.raceid = r.raceid AND o.statepostal = r.statepostal
            GROUP BY r.raceid, r.statepostal, r.officeid, r.national, o.race_unique_id, o.accept_ap_calls
;"""

ELEX_RESULTS_VIEW_COMMAND = """
CREATE OR REPLACE VIEW elex_results as
    SELECT orace.race_unique_id, orace.report, orace.nyt_race_name, orace.nyt_race_description, orace.accept_ap_calls, orace.nyt_called, ocand.nyt_winner,ocand.nyt_name, result.* FROM results as result
        JOIN override_candidates as ocand on result.candidate_unique_id = ocand.candidate_unique_id and result.statepostal = ocand.statepostal and result.raceid = ocand.raceid
        JOIN override_races as orace on orace.statepostal = result.statepostal and orace.raceid = result.raceid
;"""

def make_field(cls, field_name):
    return (field_name, getattr(cls, field_name))

def update_views(database):
    """
    Resets the Postgres VIEWs.
    """
    database.execute_sql(ELEX_RESULTS_VIEW_COMMAND)
    database.execute_sql(ELEX_RACE_VIEW_COMMAND)

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