from flask import request, abort, Blueprint, render_template, jsonify
# from utils.mongodb import 
from typing import Union
import json

liff_blueprint = Blueprint('liff', __name__, template_folder='../templates', static_folder='../static')

@liff_blueprint.route("/")
def liff():

    return render_template('history.html')
