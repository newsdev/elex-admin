#!/usr/bin/env python

import argparse
import glob
import json
import os
import re

from flask import Flask, render_template, request

import models
import utils

app = Flask(__name__)

def update_views():
    models.database.execute_sql(utils.ELEX_RESULTS_VIEW_COMMAND)
    models.database.execute_sql(utils.ELEX_RACE_VIEW_COMMAND)
    models.database.execute_sql(utils.ELEX_CANDIDATE_VIEW_COMMAND)

def clean_payload(payload):
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
    for k,v in payload.items():
        setattr(cls,k,v)
    cls.save()

def set_winner(candidateid, raceid):
    print candidateid, raceid

def build_context():
    context = {}
    context['CDN_URL'] = utils.CDN_URL
    context['RACEDATE'] = utils.RACEDATE
    return dict(context)

@app.route('/elex/')
def race_list():
    context = build_context()
    context['races'] = models.ElexRace.select()
    return render_template('race_list.html', **context)

@app.route('/elex/race/<raceid>/', methods=['GET', 'POST'])
def race_detail(raceid):
    if request.method == 'GET':
        context = build_context()
        context['race'] = models.ElexRace.get(models.ElexRace.raceid == raceid)
        context['candidates'] = models.ElexCandidate.select().where(models.ElexCandidate.nyt_races.contains(int(raceid)))
        return render_template('race_detail.html', **context)

    if request.method == 'POST':
        payload = clean_payload(dict(request.form))
        try:
            r = models.OverrideRace.get(models.OverrideRace.race_raceid == raceid)
        except models.OverrideRace.DoesNotExist:
            r = models.OverrideRace.create(race_raceid=raceid)

        if payload.get('nyt_winner', None):
            set_winner(payload['nyt_winner'], raceid)

        update_model(r, payload)
        update_views()

        return json.dumps({"message": "success"})

@app.route('/elex/candidate/<candidateid>/', methods=['POST'])
def candidate_detail(candidateid):
    if request.method == 'POST':
        payload = clean_payload(dict(request.form))

        try:
            oc = models.OverrideCandidate.get(models.OverrideCandidate.candidate_candidateid == candidateid)
        except models.OverrideCandidate.DoesNotExist:
            oc = models.OverrideCandidate.create(candidate_candidateid=candidateid)

        update_model(oc, payload)
        update_views()

        return json.dumps({"message": "success"})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port')
    args = parser.parse_args()
    server_port = 8001

    if args.port:
        server_port = int(args.port)

    app.run(host='0.0.0.0', port=server_port, debug=True)