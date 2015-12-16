#!/usr/bin/env python

import argparse
import glob
import json
import os
import re

from flask import Flask, render_template, request

import models

app = Flask(__name__)

CDN_URL = os.environ.get('ELEX_ADMIN_CDN_URL', None)
ELEX_CANDIDATE_VIEW_COMMAND = """CREATE OR REPLACE VIEW elex_candidate as
   SELECT c.*, r.* from candidates as r
       LEFT JOIN override_candidates as c on r.candidateid = c.candidate_unique_id
;"""
ELEX_RESULTS_VIEW_COMMAND = """CREATE OR REPLACE VIEW elex_results as
   SELECT o.*, c.*, r.* from results as r
       LEFT JOIN override_candidates as c on r.candidateid = c.candidate_unique_id
       LEFT JOIN override_races as o on r.raceid = o.race_raceid
;"""

def build_context():
    context = {}
    context['CDN_URL'] = CDN_URL
    return dict(context)

@app.route('/elex/')
def race_list():
    context = build_context()
    context['races'] = models.ElexRace.select()
    return render_template('race_list.html', **context)

@app.route('/elex/race/<raceid>/')
def race_detail(raceid):
    context = build_context()
    context['race'] = models.ElexRace.get(models.ElexRace.raceid == raceid)
    context['candidates'] = models.ElexCandidate.select().where(models.ElexCandidate.nyt_races.contains(int(raceid)))
    return render_template('race_detail.html', **context)

@app.route('/elex/candidate/<candidateid>/', methods=['POST'])
def candidate_detail(candidateid):
    payload = dict(request.form)
    try:
        oc = models.OverrideCandidate.get(models.OverrideCandidate.candidate_unique == candidateid)
    except models.OverrideCandidate.DoesNotExist:
        oc = models.OverrideCandidate.create(candidate_unique=candidateid)

    for k,v in payload.items():
        v = v[0]
        if v == u'':
            v = None
        setattr(oc,k,v)

    oc.save()
    models.database.execute_sql(ELEX_RESULTS_VIEW_COMMAND)
    models.database.execute_sql(ELEX_CANDIDATE_VIEW_COMMAND)
    return json.dumps({"result": "success"})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port')
    args = parser.parse_args()
    server_port = 8001

    if args.port:
        server_port = int(args.port)

    app.run(host='0.0.0.0', port=server_port, debug=True)