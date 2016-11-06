#!/usr/bin/env python

import argparse
import csv
import glob
import json
import io
import os
import re
from sets import Set
import datetime

from csvkit import py2
from flask import Flask, render_template, request, make_response, Response
import peewee
from peewee import *
from playhouse.postgres_ext import *

import general.models as models
import general.utils as utils
from maps import ELECTORAL_VOTES_BY_STATEPOSTAL

app = Flask(__name__)
app.debug=True


# These are reportingunitids since ME/NE have
# reporting units that are sub-state.
# Also removes ME/NE the state since the
# electoral votes are assigned by the reporting
# unit (e.g., at-large or congressional district 1)
# rather than at the state level.

PREZ_SWING = [
    'state-FL-1',
    'state-PA-1',
    'state-OH-1',
    'state-NC-1',
    'state-VA-1',
    'state-WI-1',
    'state-CO-1',
    'state-IA-1',
    'state-NV-1',
    'state-NH-1',
    'state-AZ-1',
    'state-GA-1',
    'state-ME-1',
    'district-20027',
    'district-28007'
]

PREZ_OTHER = [
    'state-DC-1',
    'state-HI-1',
    'state-MD-1',
    'state-VT-1',
    'state-CA-1',
    'state-NY-1',
    'state-MA-1',
    'state-RI-1',
    'state-NJ-1',
    'state-IL-1',
    'state-CT-1',
    'state-DE-1',
    'state-WA-1',
    'state-OR-1',
    'state-NM-1',
    'state-MI-1',
    'state-MN-1',
    'district-20005',
    'district-20026',
    'state-MO-1',
    'state-IN-1',
    'state-SC-1',
    'state-TX-1',
    'state-AR-1',
    'state-MS-1',
    'state-LA-1',
    'state-MT-1',
    'state-UT-1',
    'state-KS-1',
    'state-AK-1',
    'state-SD-1',
    'state-TN-1',
    'state-ND-1',
    'state-AL-1',
    'state-KY-1',
    'state-OK-1',
    'state-ID-1',
    'state-WV-1',
    'state-WY-1',
    'district-28004',
    'district-28006',
    'district-28008'
]

SENATE_SWING = ['WI','IN','NV','NH','PA','NC','MO'] 
SENATE_OTHER = ['FL','AZ','LA','KY','IA','AR','OH','GA','AL','SD','OK','ND','UT','KS','SC','ID','AK', 'CA','VT','NY','MD','HI','CT','OR','WA','CO','IL']

ALL_STATES = [x for x in SENATE_SWING + SENATE_OTHER]


@app.route('/elections/2016/admin/<racedate>/archive/')
def archive_list(racedate):
    racedate_db = PostgresqlExtDatabase('elex_%s' % racedate,
        user=os.environ.get('ELEX_ADMIN_USER', 'elex'),
        host=os.environ.get('ELEX_ADMIN_HOST', '127.0.0.1')
    )
    models.database_proxy.initialize(racedate_db)
    context = utils.build_context(racedate)
    context['files'] = sorted(
        [
            {
                "name": f.split('/')[-1],
                "date": datetime.datetime.fromtimestamp(float(f.split('/')[-1].split('-')[-1].split('.json')[0]))
            }
            for f in glob.glob('/tmp/%s/*.json' % racedate)
        ],
        key=lambda x:x,
        reverse=True
    )[:750]

    context['states'] = []

    state_list = sorted(list(Set([race.statepostal for race in models.ElexRace.select()])), key=lambda x: x)

    for state in state_list:
        race = models.ElexRace.select().where(models.ElexRace.statepostal == state)[0]
        state_dict = {}
        state_dict['statepostal'] = state
        state_dict['report'] = race.report
        state_dict['report_description'] = race.report_description
        context['states'].append(state_dict)

    return render_template('archive_list.html', **context)

@app.route('/elections/2016/admin/<racedate>/archive/<filename>')
def archive_detail(racedate, filename):
    with open('/tmp/%s/%s' % (racedate, filename), 'r') as readfile:
        return readfile.read()


@app.route('/elections/2016/admin/<racedate>/loader/timeout/', methods=['POST'])
def set_loader_timeout(racedate):
    if request.method == 'POST':
        payload = utils.clean_payload(dict(request.form))

        timeout = payload.get('timeout', '')
        os.system('echo export ELEX_LOADER_TIMEOUT=%s > /tmp/elex_loader_timeout.sh' % timeout)

        return json.dumps({"message": "success", "output": "0"})


@app.route('/elections/2016/admin/<racedate>/actions/call-race/', methods=['POST'])
def action_call_race(racedate):
    if request.method == "POST":
        racedate_db = PostgresqlExtDatabase('elex_%s' % racedate,
                user=os.environ.get('ELEX_ADMIN_USER', 'elex'),
                host=os.environ.get('ELEX_ADMIN_HOST', '127.0.0.1')
        )
        models.database_proxy.initialize(racedate_db)

        payload = utils.clean_payload(dict(request.form))

        if payload['statepostal'] in ['ME', 'NE']:
            payload['nyt_electwon'] = ELECTORAL_VOTES_BY_STATEPOSTAL[payload['reportingunitid']]
        else:
            payload['nyt_electwon'] = ELECTORAL_VOTES_BY_STATEPOSTAL[payload['statepostal']]

        print payload['nyt_electwon']

        UPDATE_PREZ_LOSERS = """
            UPDATE override_candidates
                SET nyt_winner = FALSE, nyt_electwon = 0
                    WHERE reportingunitid = '%(reportingunitid)s'
                    AND raceid = '%(raceid)s';
        """ % payload

        UPDATE_PREZ_WINNER = """
            UPDATE override_candidates
                SET nyt_winner = TRUE, nyt_electwon = %(nyt_electwon)s
                    WHERE statepostal = '%(statepostal)s'
                    AND raceid = '%(raceid)s'
                    AND candidate_unique_id = '%(candidate_unique_id)s'
                    AND reportingunitid = '%(reportingunitid)s';
            """ % payload

        UPDATE_LOSERS = """
            UPDATE override_candidates
                SET nyt_winner = FALSE
                    WHERE statepostal = '%(statepostal)s'
                    AND raceid = '%(raceid)s';
        """ % payload

        UPDATE_WINNER = """
            UPDATE override_candidates
                SET nyt_winner = TRUE
                    WHERE statepostal = '%(statepostal)s'
                    AND raceid = '%(raceid)s'
                    AND candidate_unique_id = '%(candidate_unique_id)s';
            """ % payload

        SET_RACE_TRUE = """
            UPDATE override_races 
                SET nyt_called = TRUE
                    WHERE race_unique_id = '%(statepostal)s-%(raceid)s'
                    AND reportingunitid = '%(reportingunitid)s';
        """ % payload

        SET_RACE_FALSE = """
            UPDATE override_races 
                SET nyt_called = FALSE
                    WHERE race_unique_id = '%(statepostal)s-%(raceid)s'
                    AND reportingunitid = '%(reportingunitid)s';
        """ % payload

        if payload['raceid'] == '0':
            models.database_proxy.execute_sql(UPDATE_PREZ_LOSERS)
        else:
            models.database_proxy.execute_sql(UPDATE_LOSERS)

        if payload['candidate_unique_id']:
            if payload['raceid'] == '0':
                models.database_proxy.execute_sql(UPDATE_PREZ_WINNER)
            else:
                models.database_proxy.execute_sql(UPDATE_WINNER)

            models.database_proxy.execute_sql(SET_RACE_TRUE)
        else:
            models.database_proxy.execute_sql(SET_RACE_FALSE)

        utils.update_views(models.database_proxy)

        return json.dumps({"message": "success", "result": "called %(race_unique_id)s for %(candidate_unique_id)s" % payload})

@app.route('/elections/2016/admin/<racedate>/actions/ap/', methods=['POST'])
def action_ap(racedate):
    if request.method == "POST":
        racedate_db = PostgresqlExtDatabase('elex_%s' % racedate,
                user=os.environ.get('ELEX_ADMIN_USER', 'elex'),
                host=os.environ.get('ELEX_ADMIN_HOST', '127.0.0.1')
        )
        models.database_proxy.initialize(racedate_db)

        payload = utils.clean_payload(dict(request.form))

        UPDATE_QUERY = """
            UPDATE override_races
                SET accept_ap_calls = %(accept_ap_calls)s
                    WHERE raceid = '%(raceid)s'
                    AND statepostal = '%(statepostal)s'
                    AND reportingunitid = '%(reportingunitid)s';""" % payload

        models.database_proxy.execute_sql(UPDATE_QUERY)
        models.database_proxy.execute_sql(utils.ELEX_RACE_VIEW_COMMAND)

        return json.dumps({"message": "success", "result": "ap_calls %(accept_ap_calls)s for %(statepostal)s" % payload})

@app.route('/elections/2016/admin/<racedate>/')
def race_list(racedate):
    context = utils.build_context(racedate)

    context['SLACK_WEBHOOK_URL'] = os.environ.get('SLACK_WEBHOOK_URL', None)

    context['prez_swing'] = []
    context['prez_other'] = []
    context['senate'] = []
    context['house'] = []
    context['governor'] = []

    try:
        racedate_db = PostgresqlExtDatabase('elex_%s' % racedate,
                user=os.environ.get('ELEX_ADMIN_USER', 'elex'),
                host=os.environ.get('ELEX_ADMIN_HOST', '127.0.0.1')
        )
        models.database_proxy.initialize(racedate_db)

        context['states'] = sorted(ALL_STATES, key=lambda x:x)

        try:
            context['ap_winners'] = [{'reportingunitid': w.reportingunitid, 'statepostal': w.statepostal, 'raceid': w.raceid, 'candidate_unique_id': w.candidate_unique_id} for w in models.ElexResult.select(models.ElexResult.reportingunitid, models.ElexResult.statepostal, models.ElexResult.raceid, models.ElexResult.candidate_unique_id).distinct().where(models.ElexResult.officeid << ["P","S"],models.ElexResult.level << ['state','district'],models.ElexResult.winner == True)]
        except models.ElexResult.DoesNotExist:
            context['ap_winners'] = []

        try:
            context['nyt_winners'] = [{'reportingunitid': w.reportingunitid, 'statepostal': w.statepostal, 'raceid': w.raceid, 'candidate_unique_id': w.candidate_unique_id} for w in models.ElexResult.select(models.ElexResult.reportingunitid, models.ElexResult.statepostal, models.ElexResult.raceid, models.ElexResult.candidate_unique_id).where(models.ElexResult.officeid << ["P","S"],models.ElexResult.level << ['state','district'],models.ElexResult.nyt_winner == True)]
        except models.ElexResult.DoesNotExist:
            context['nyt_winners'] = []

        context['prez_cands'] = [e for e in models.ElexResult\
                                    .select().distinct()\
                                    .where(
                                        models.ElexResult.raceid == "0",
                                        models.ElexResult.level == "state",
                                        models.ElexResult.party << ['Dem', 'GOP']
                                    )]

        for e in models.ElexResult\
                        .select(
                            models.ElexResult.raceid,
                            models.ElexResult.party,
                            models.ElexResult.level,
                            models.ElexResult.reportingunitid,
                            models.ElexResult.last,
                            models.ElexResult.first,
                            models.ElexResult.candidate_unique_id
                        ).distinct()\
                        .where(
                            models.ElexResult.raceid == "0",
                            models.ElexResult.level == "district",
                            models.ElexResult.party << ['Dem', 'GOP']
                        ):
                            context['prez_cands'].append(e)

        context['prez_cands'] = sorted([e for e in context['prez_cands']], key=lambda x: x.statepostal)

        context['prez_swing'] = models.OverrideRace\
                                    .select()\
                                    .where(
                                        models.OverrideRace.raceid == "0",
                                        models.OverrideRace.reportingunitid << PREZ_SWING
                                    )\
                                    .order_by(+models.OverrideRace.statepostal, +models.OverrideRace.reportingunitid)

        context['prez_other'] = models.OverrideRace\
                                    .select()\
                                    .where(
                                        models.OverrideRace.raceid == "0",
                                        models.OverrideRace.reportingunitid << PREZ_OTHER
                                    )\
                                    .order_by(+models.OverrideRace.statepostal, +models.OverrideRace.reportingunitid)

        context['senate_swing'] = models.ElexRace\
                                    .select()\
                                    .where(
                                        models.ElexRace.officeid == "S",
                                        models.ElexRace.statepostal << SENATE_SWING
                                    )\
                                    .order_by(+models.ElexRace.statepostal)

        context['senate_swing_cands'] = models.ElexResult\
                                    .select()\
                                    .where(
                                        models.ElexResult.officeid == "S",
                                        models.ElexResult.statepostal << SENATE_SWING,
                                        models.ElexResult.party << ["Dem", "GOP"],
                                        models.ElexResult.level == 'state'
                                    )\
                                    .order_by(+models.ElexResult.statepostal, +models.ElexResult.last)

        context['senate_other'] = models.ElexRace\
                                    .select()\
                                    .where(
                                        models.ElexRace.national == True,
                                        models.ElexRace.officeid == "S",
                                        models.ElexRace.statepostal << SENATE_OTHER,
                                    )\
                                    .order_by(+models.ElexRace.statepostal)

        context['senate_other_cands'] = models.ElexResult\
                                    .select()\
                                    .where(
                                        models.ElexResult.national == True,
                                        models.ElexResult.officeid == "S",
                                        models.ElexResult.statepostal << SENATE_OTHER,
                                        models.ElexResult.party << ["Dem", "GOP"],
                                        models.ElexResult.level == 'state'
                                    )\
                                    .order_by(+models.ElexResult.statepostal)

        return render_template('dashboard.html', **context)

    except peewee.OperationalError, e:
        context['error'] = e
        return render_template('error.html', **context)

    except peewee.ProgrammingError, e:
        context['error'] = e
        return render_template('error.html', **context)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port')
    args = parser.parse_args()
    server_port = 8001

    if args.port:
        server_port = int(args.port)

    app.run(host='0.0.0.0', port=server_port, debug=True)