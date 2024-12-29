from flask import request, Blueprint, render_template, jsonify, redirect, url_for, session
from typing import Union
import json
import os
import requests

from utils.mongodb import mongo_home_by_id, mongo_find_user, house_by_id

liff_blueprint = Blueprint('liff', __name__, template_folder='../templates', static_folder='../static')

LIFF_ID = os.environ['LIFF_ID']

@liff_blueprint.route("/")
def liff():
    access_token = request.args.get('access_token')
    if access_token:
        # Redirect to the /check route for authentication
        return redirect(url_for('liff.check', access_token=access_token))
    else:
        # Render a default page or redirect to login if no token is provided
        house_collected = []
        data = {
            'text': 'Loading.',
            'collected': house_collected
        }
        return render_template('check.html', liff_id=LIFF_ID, data=data)
        # return render_template('history.html', liff_id=LIFF_ID, data=data)

@liff_blueprint.route('/check')
def check():
    access_token = request.args.get('access_token')
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.line.me/v2/profile', headers=headers)

    if response.status_code == 200:
        profile_data = response.json()
        user_id = profile_data.get('userId')
        if user_id :
            session['user_id'] = user_id
            return redirect(url_for('liff.user_page'))
        else:
            return jsonify({'error': 'User ID not found'}), 404
    else:
        return jsonify({'error': 'Failed to fetch profile'}), response.status_code

@liff_blueprint.route('/history')
def user_page():
    user_id = session.get('user_id')  # Retrieve user_id from session
    house_collected = []

    if not user_id:
        # If no user_id is in the session, redirect back to login or home
        return redirect(url_for('liff.liff'))
    
    home_json = mongo_find_user(user_id)
    if home_json!="[]":
        home_id = json.loads(home_json)[0]['home_id']
        house_json = house_by_id(home_id)
        try :
            house_collected = json.loads(house_json)['collected']
            data = {
                'text': 'Here is collected data.',
                'collected': house_collected
            }
        except Exception as e:
            data = {
                'text': 'There is no collected data yet.',
                'collected': house_collected
            }
    else :
        data = {
            'text': 'This Account is not register yet.',
            'collected': house_collected
        }

    return render_template('history.html', data=data, liff_id=LIFF_ID)
