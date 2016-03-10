#!/usr/bin/env python

import argparse
import csv
import glob
import json
import io
import os
import re
from sets import Set

from csvkit import py2
from flask import Flask, render_template, request, make_response, Response

import models
import utils

app = Flask(__name__)
app.debug=True

@app.route('/elections/2016/admin/<racedate>/archive/')
def archive_list(racedate):
    context = utils.build_context(racedate)
    context['files'] = sorted([f.split('/')[-1] for f in glob.glob('/tmp/%s/*.json' % racedate)], key=lambda x:x, reverse=True)[:25]

    return render_template('archive_list.html', **context)

@app.route('/elections/2016/admin/<racedate>/archive/<filename>')
def archive_detail(racedate, filename):
    with open('/tmp/%s/%s' % (racedate, filename), 'r') as readfile:
        return readfile.read()

@app.route('/elections/2016/admin/<racedate>/')
def race_list(racedate):
    context = utils.build_context(racedate)
    context['timeout'] = os.environ.get('ELEX_LOADER_TIMEOUT', '30')
    if os.path.isfile('/tmp/elex_loader_timeout.sh'):
        with open('/tmp/elex_loader_timeout.sh') as readfile:
            context['timeout'] = readfile.read().split('=')[1].strip()

    context['presidential_races'] = models.ElexRace\
                                .select()\
                                .where(
                                    models.ElexRace.national == True, 
                                    models.ElexRace.officeid == "P"
                                )\
                                .order_by(+models.ElexRace.statepostal)

    context['national_races'] = models.ElexRace\
                                .select()\
                                .where(
                                    models.ElexRace.national == True,
                                    models.ElexRace.officeid << ["G","S","H"]
                                )\
                                .order_by(+models.ElexRace.statepostal)
    context['other_races'] = models.ElexRace\
                                .select()\
                                .where(
                                    ~(models.ElexRace.id << context['national_races']), 
                                    ~(models.ElexRace.id << context['presidential_races']), 
                                )\
                                .order_by(+models.ElexRace.statepostal)
    context['states'] = []

    state_list = sorted(list(Set([race.statepostal for race in models.ElexRace.select()])), key=lambda x: x)

    for state in state_list:
        race = models.ElexRace.select().where(models.ElexRace.statepostal == state)[0]
        state_dict = {}
        state_dict['statepostal'] = state
        state_dict['report'] = race.report
        state_dict['report_description'] = race.report_description
        context['states'].append(state_dict)

    return render_template('race_list.html', **context)

@app.route('/elections/2016/admin/<racedate>/script/<script_type>/', methods=['GET'])
def scripts(racedate, script_type):
    base_command = '. /home/ubuntu/.virtualenvs/elex-loader/bin/activate && cd /home/ubuntu/elex-loader/ && '
    if request.method == 'GET':
        o = "1"

        if script_type == 'bake':
            pass
        else:
            o = os.system('%s./scripts/prd/%s.sh %s' % (base_command, script_type, racedate))

        return json.dumps({"message": "success", "output": o})

@app.route('/elections/2016/admin/<racedate>/csv/', methods=['POST'])
def overrides_post(racedate):
    if request.method == 'POST':
        payload = dict(request.form)
        candidates_text = None
        races_text = None

        if payload.get('candidates_text', None):
            candidates_text = str(payload['candidates_text'][0])

        if payload.get('races_text', None):
            races_text = str(payload['races_text'][0])

        if races_text:
            with open('../elex-loader/overrides/%s_override_races.csv' % racedate, 'w') as writefile:
                writefile.write(races_text)

        if candidates_text:
            with open('../elex-loader/overrides/%s_override_candidates.csv' % racedate, 'w') as writefile:
                writefile.write(candidates_text)

        return json.dumps({"message": "success"})

@app.route('/elections/2016/admin/<racedate>/csv/<override>/', methods=['GET'])
def overrides_csv(racedate, override):
    if request.method == 'GET':
        output = ''

        if override == 'race':
            objs = [r.serialize() for r in models.OverrideRace.select()]

        if override == 'candidate':
            objs = [r.serialize() for r in models.OverrideCandidate.select()]

        output = io.BytesIO()
        fieldnames = [unicode(k) for k in objs[0].keys()]
        writer = py2.CSVKitDictWriter(output, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(objs)
        output = make_response(output.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=override_%ss.csv" % override
        output.headers["Content-type"] = "text/csv"
        return output

@app.route('/elections/2016/admin/<racedate>/state/<statepostal>/', methods=['POST'])
def state_detail(racedate, statepostal):
    if request.method == 'POST':
        payload = utils.clean_payload(dict(request.form))
        races = [r.raceid for r in models.ElexRace.select().where(models.ElexRace.statepostal == statepostal)]
        r = models.OverrideRace.update(report=payload['report'], report_description=payload['report_description']).where(models.OverrideRace.race_raceid << races)
        r.execute()
        utils.update_views(models.database)

        return json.dumps({"message": "success"})

@app.route('/elections/2016/admin/<racedate>/race/<raceid>/', methods=['GET', 'POST'])
def race_detail(racedate, raceid):
    if request.method == 'GET':
        context = utils.build_context(racedate)
        context['race'] = models.ElexRace.get(models.ElexRace.raceid == raceid)
        context['candidates'] = sorted(models.ElexCandidate.select().where(models.ElexCandidate.nyt_races.contains(int(raceid))), key=lambda x:x.nyt_display_order)

        context['ap_winner'] = None
        ap_winner = models.ElexResult.select().where(models.ElexResult.raceid == raceid, models.ElexResult.winner == True)
        if len(ap_winner) > 0:
            context['ap_winner'] = ap_winner[0]

        context['states'] = []

        state_list = sorted(list(Set([race.statepostal for race in models.ElexRace.select()])), key=lambda x: x)

        for state in state_list:
            race = models.ElexRace.select().where(models.ElexRace.statepostal == state)[0]
            state_dict = {}
            state_dict['statepostal'] = state
            state_dict['report'] = race.report
            state_dict['report_description'] = race.report_description
            context['states'].append(state_dict)

        return render_template('race_detail.html', **context)

    if request.method == 'POST':
        payload = utils.clean_payload(dict(request.form))
        try:
            r = models.OverrideRace.get(models.OverrideRace.race_raceid == raceid)
        except models.OverrideRace.DoesNotExist:
            r = models.OverrideRace.create(race_raceid=raceid)

        utils.set_winner(payload['nyt_winner'], raceid)

        utils.update_model(r, payload)
        utils.update_views(models.database)

        return json.dumps({"message": "success"})

@app.route('/elections/2016/admin/<racedate>/candidateorder/', methods=['POST'])
def candidate_order(racedate):
    if request.method == 'POST':
        payload = utils.clean_payload(dict(request.form))

        if payload.get('candidates', None):
            print payload['candidates']
            for idx, candidateid in enumerate(payload['candidates'].split(',')):
                oc = models.OverrideCandidate.update(nyt_display_order=idx).where(models.OverrideCandidate.candidate_candidateid == candidateid)
                oc.execute()

        utils.update_views(models.database)

        return json.dumps({"message": "success"})

@app.route('/elections/2016/admin/<racedate>/candidate/<candidateid>/', methods=['POST'])
def candidate_detail(racedate, candidateid):
    if request.method == 'POST':
        payload = utils.clean_payload(dict(request.form))

        try:
            oc = models.OverrideCandidate.get(models.OverrideCandidate.candidate_candidateid == candidateid)
        except models.OverrideCandidate.DoesNotExist:
            oc = models.OverrideCandidate.create(candidate_candidateid=candidateid)

        utils.update_model(oc, payload)
        utils.update_views(models.database)

        return json.dumps({"message": "success"})

@app.route('/elections/2016/admin/<racedate>/loader/timeout/', methods=['POST'])
def set_loader_timeout(racedate):
    if request.method == 'POST':
        payload = utils.clean_payload(dict(request.form))

        timeout = payload.get('timeout', '')
        os.system('echo export ELEX_LOADER_TIMEOUT=%s > /tmp/elex_loader_timeout.sh' % timeout)

        return json.dumps({"message": "success"})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port')
    args = parser.parse_args()
    server_port = 8001

    if args.port:
        server_port = int(args.port)

    app.run(host='0.0.0.0', port=server_port, debug=True)