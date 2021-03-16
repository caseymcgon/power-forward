from flask import Flask, Response, request, abort, jsonify, render_template, session
import json
import logging
import os

import requests
import yaml

from src.gateway import *
from src.models.shared import *

def create_app(config=None):
    app = Flask(__name__)
    # load app sepcified configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)
    # setup_app(app)
    return app

# def setup_app(app):
    # Create tables if they do not exist already
    # @app.before_first_request
    # def create_tables():
    #     db.create_all()

    # session = flask_scoped_session(session_factory, app)
    # db.init_app(app)
    # config_oauth(app)
    # app.register_blueprint(bp, url_prefix='')

app = create_app({
    'SECRET_KEY': 'secret',
    'SQLALCHEMY_TRACK_MODIFICATIONS': True,
    # 'SQLALCHEMY_DATABASE_URI': DB_CONNECTION_STRING,
})


@app.route('/')
def index():
    analytics(request)
    return render_template('index.html', title='Home')

@app.route('/__healthcheck__', methods=['GET', 'POST'])
def health_check():
    '''
    Health check responds for GET and POST
    GET: returns time time of server receiving request.
    POST: echos parameters and data passeed by request.
    '''
    ## Query parameter argumeents
    query_string_params = request.args

    ## data parameters from http request
    data_params = request.get_json()
    print(data_params)
    if request.method == 'GET':
        posted = { 'params': query_string_params, 'data': data_params}
        return render_template( 'healthcheck.html',
                                title='Healthcheck',
                                ttr={'time of response': time.time(), 'date': datetime.now()},
                                echo=posted)

    if request.method == 'POST':
        form_param = request.form['form_param']
        posted = { 'params': query_string_params, 'data': data_params , 'form_param': form_param}
        return render_template( 'healthcheck.html',
                                title='Healthcheck',
                                ttr={'time of response': time.time(), 'date': datetime.now()},
                                echo=posted)

@app.route('/team')
def display_team():
    return render_template('team.html', title='Team')

@app.route('/map')
def display_map():
    return render_template('map.html', title='Map')

@app.route('/discord', methods=['GET', 'POST'])
def discord():
    '''
    Require a specific token "X-POWER-FORWARD-TOKEN"
    in order to access a page that sends a message directly
    to the discord channel.
    '''
    ## validate a token X-POWER-FORWARD-TOKEN to send direct discord messages
    successful, msg = validate_PF_API_token(request.headers)
    if (not successful):
            # abort(401, success_msg)
            return Response(response={ msg },
                            status=401), 400, {'ContentType':'application/json'}

    if request.method == 'GET':
        return render_template('discord.html', title='Discord messaging')
    if request.method == 'POST':
        ## extract username and message from form
        username = request.form['username']
        message = request.form['message']

        payload = {
            'username': "Justin's Local",
            'avatar_url': "",
            'content': message
        }
        send_to_discord(payload)
        return "pshed"

@app.errorhandler(500)
def server_error(e):
    analytics(request)
    logging.exception("Error :/")
    return """
    Idk, server error :/
    <pre>{}</pre>
    sorry
    """.format(e), 500
