import glob
import os

CDN_URL = os.environ.get('ELEX_ADMIN_CDN_URL', 'https://int.nyt.com/cdn')

ELEX_RACE_VIEW_COMMAND = """
CREATE OR REPLACE VIEW elex_races AS
    SELECT DISTINCT r.raceid, r.reportingunitid, r.statepostal, r.officeid, r.national, o.race_unique_id, o.accept_ap_calls
        FROM results AS r
            LEFT JOIN override_races AS o ON o.raceid = r.raceid AND o.statepostal = r.statepostal AND o.reportingunitid = r.reportingunitid
            WHERE r.level IN ('state', 'district')
            GROUP BY r.raceid, r.reportingunitid, r.statepostal, r.officeid, r.national, o.race_unique_id, o.accept_ap_calls
;"""

ELEX_RESULTS_VIEW_COMMAND = """
CREATE OR REPLACE VIEW elex_results as
(SELECT DISTINCT orace.race_unique_id, orace.report, orace.nyt_race_name, orace.nyt_race_description, orace.accept_ap_calls, orace.nyt_called, ocand.nyt_winner,ocand.nyt_name, ocand.nyt_electwon, result.* FROM results as result
        LEFT JOIN override_candidates as ocand on result.candidate_unique_id = ocand.candidate_unique_id and result.statepostal = ocand.statepostal and result.raceid = ocand.raceid
        LEFT JOIN override_races as orace on orace.statepostal = result.statepostal and orace.raceid = result.raceid
        WHERE result.raceid != '0') UNION (SELECT DISTINCT orace.race_unique_id, orace.report, orace.nyt_race_name, orace.nyt_race_description, orace.accept_ap_calls, orace.nyt_called, ocand.nyt_winner,ocand.nyt_name, ocand.nyt_electwon, result.* FROM results as result
        LEFT JOIN override_candidates as ocand on result.candidate_unique_id = ocand.candidate_unique_id and result.statepostal = ocand.statepostal and result.raceid = ocand.raceid AND ocand.reportingunitid = result.reportingunitid
        LEFT JOIN override_races as orace on orace.statepostal = result.statepostal and orace.raceid = result.raceid and orace.reportingunitid = result.reportingunitid
        WHERE result.raceid = '0');
"""

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
            models.OverrideRace.race_unique_id==raceid
        )
        nc = models.OverrideCandidate\
                .update(nyt_winner=False)\
                .where(
                    models.OverrideCandidate.candidate_unique_id != candidateid,
                    models.OverrideCandidate.raceid==raceid.split('-')[1]
                )
        yc = models.OverrideCandidate\
                .update(nyt_winner=True)\
                .where(
                    models.OverrideCandidate.candidate_unique_id == candidateid,
                    models.OverrideCandidate.raceid==raceid.split('-')[1]
                )

        r.execute()
        nc.execute()
        yc.execute()
    else:
        r = models.OverrideRace.update(nyt_called=False).where(
            models.OverrideRace.race_unique_id==raceid
        )
        nc = models.OverrideCandidate\
                .update(nyt_winner=False)\
                .where(models.OverrideCandidate.raceid==raceid.split('-')[1])
        r.execute()
        nc.execute()

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

def build_context(racedate, raceyear):
    """
    Every page needs these two things.
    """
    context = {}
    context['CDN_URL'] = CDN_URL
    context['RACEDATE'] = racedate
    context['RACEYEAR'] = raceyear
    context['race_dates'] = sorted([d.split('/')[-1].split('.ini')[0] for d in glob.glob('elex_admin/*.ini')], key=lambda x:x)
    context['timeout'] = os.environ.get('ELEX_LOADER_TIMEOUT', '30')
    if os.path.isfile('/tmp/elex_loader_timeout.sh'):
        with open('/tmp/elex_loader_timeout.sh') as readfile:
            context['timeout'] = readfile.read().split('=')[1].strip()
    return dict(context)
