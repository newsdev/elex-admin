import os

RACEDATE = os.environ.get('RACEDATE', None)
CDN_URL = os.environ.get('ELEX_ADMIN_CDN_URL', None)

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