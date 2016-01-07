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

@app.route('/elections/2016/admin/')
def race_list():
    context = utils.build_context()
    context['races'] = models.ElexRace.select()
    return render_template('race_list.html', **context)

@app.route('/elections/2016/admin/race/<raceid>/', methods=['GET', 'POST'])
def race_detail(raceid):
    if request.method == 'GET':
        context = utils.build_context()
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
            utils.set_winner(payload['nyt_winner'], raceid)

        utils.update_model(r, payload)
        utils.update_views(models.database)

        return json.dumps({"message": "success"})

@app.route('/elections/2016/admin/candidate/<candidateid>/', methods=['POST'])
def candidate_detail(candidateid):
    if request.method == 'POST':
        payload = utils.clean_payload(dict(request.form))

        try:
            oc = models.OverrideCandidate.get(models.OverrideCandidate.candidate_candidateid == candidateid)
        except models.OverrideCandidate.DoesNotExist:
            oc = models.OverrideCandidate.create(candidate_candidateid=candidateid)

        utils.update_model(oc, payload)
        utils.update_views(models.database)

        return json.dumps({"message": "success"})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port')
    args = parser.parse_args()
    server_port = 8001

    if args.port:
        server_port = int(args.port)

    app.run(host='0.0.0.0', port=server_port, debug=True)