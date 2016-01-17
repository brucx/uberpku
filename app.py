# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from example.utils import import_app_credentials

from uber_rides.auth import AuthorizationCodeGrant
from uber_rides.client import UberRidesClient
from uber_rides.session import Session, OAuth2Credential


from datetime import datetime

from flask import Flask, request, redirect, render_template, jsonify

from views.todos import todos_view

import api

app = Flask(__name__)

# 动态路由
app.register_blueprint(todos_view, url_prefix='/todos')
credentials = import_app_credentials()


@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-type'
    return response

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/time')
def time():
    return str(datetime.now())


@app.route('/login')
def login():
    auth_flow = AuthorizationCodeGrant(
        credentials.get('client_id'),
        credentials.get('scopes'),
        credentials.get('client_secret'),
        credentials.get('redirect_url'),
    )
    auth_url = auth_flow.get_authorization_url()

    return redirect(auth_url)


@app.route('/oauth')
def oauth():
    auth_flow = AuthorizationCodeGrant(
    credentials.get('client_id'),
    credentials.get('scopes'),
    credentials.get('client_secret'),
    credentials.get('redirect_url'),
    )
    session = auth_flow.get_session(request.url)
    oauth2credential = session.oauth2credential
    token = {
        "client_id":oauth2credential.client_id,
        "access_token":oauth2credential.access_token,
        "expires_in_seconds": oauth2credential.expires_in_seconds,
        "scopes": list(oauth2credential.scopes),
        "grant_type": oauth2credential.grant_type,
        "redirect_url": oauth2credential.redirect_url,
        "client_secret": oauth2credential.client_secret,
        "refresh_token": oauth2credential.refresh_token,
    }
    client = UberRidesClient(session)
    response = client.get_user_profile()
    profile = response.json
    uuid = profile.get('uuid')
    api.set_token(uuid,token)
    return render_template('oauth.html', uuid=uuid, token=token)


@app.route('/history')
def history():
    uuid = request.args.get('uuid', '')
    client = get_client_by_uid(uuid)
    response = client.get_user_activity()
    reslut = response.json
    return jsonify(reslut)


@app.route('/plan', methods=["POST", "GET"])
def plan():
    if request.method == "POST":
        uuid = request.form["uid"]
        budget_money = request.form["budget_money"]
        budget_cal = request.form["budget_cal"]

        #api.set_activity(uuid,"MONTH",budget_money,budget_cal)
        return uuid+" " +budget_money+" "+budget_cal+"\n"

    else:
        return "GET /plan under construction"


@app.route('/place', methods=["POST", "GET"])
def place():
    if request.method == "POST":
        obj = request.json
        uid = obj["uid"]
        name = obj["name"]
        latitude = obj["latitude"]
        longitude = obj["longitude"]
        api.set_profile(uid,{name:{"latitude":latitude, "longitude":longitude}})
        return ''

    else:
        uid = request.args.get('uid', '')
        name = request.args.get('name', '')
        obj = api.get_profile(uid)
        latitude = obj[name]["latitude"]
        longitude = obj[name]["longitude"]

        return jsonify({
             "name": name,
             "latitude": latitude,
             "longitude": longitude
        })


@app.route('/price')
def price():
    uuid = request.args.get('uuid', '')
    client = get_client_by_uid(uuid)
    response = client.get_price_estimates(39.979567,116.310399,39.758488,116.357046)

    result = response.json
    return jsonify(result)


@app.route('/duration')
def duration():
    uuid = request.args.get('uuid', '')
    client = get_client_by_uid(uuid)
    response = client.estimate_ride("0ed2dbad-c769-41f5-b66d-0767da627f9e",39.979567,116.310399,39.758488,116.357046)

    result = response.json
    return jsonify(result)


def get_client_by_uid(uid):
    token = api.get_token(uid)
    oauth2credential = OAuth2Credential(
        token.get("client_id"),
        token.get("access_token"),
        token.get("expires_in_seconds"),
        set(token.get("scopes")),
        token.get("grant_type"),
        token.get("redirect_url"),
        token.get("client_secret"),
        token.get("refresh_token"),
    )
    session = Session(oauth2credential=oauth2credential)
    client = UberRidesClient(session)
    return client
