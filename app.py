# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from yaml import safe_dump

from example import utils
from example.utils import success_print
from example.utils import import_app_credentials

from uber_rides.auth import AuthorizationCodeGrant
from uber_rides.client import UberRidesClient

from datetime import datetime

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask import render_template

from views.todos import todos_view

app = Flask(__name__)

# 动态路由
app.register_blueprint(todos_view, url_prefix='/todos')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/time')
def time():
    return str(datetime.now())


@app.route('/login')
def login():
    credentials = import_app_credentials()

    auth_flow = AuthorizationCodeGrant(
    credentials.get('client_id'),
    credentials.get('scopes'),
    credentials.get('client_secret'),
    credentials.get('redirect_url'),
    )

    auth_url = auth_flow.get_authorization_url()
    return '{ "auth_url" : "%s" }' % auth_url


@app.route('/oauth')
def oauth():
    credentials = import_app_credentials()

    auth_flow = AuthorizationCodeGrant(
    credentials.get('client_id'),
    credentials.get('scopes'),
    credentials.get('client_secret'),
    credentials.get('redirect_url'),
    )
    session = auth_flow.get_session(request.url)

    client = UberRidesClient(session, sandbox_mode=True)
    response = client.get_user_profile()
    profile = response.json

    uuid = profile.get('uuid')

    return render_template('oauth.html', uuid=uuid)
