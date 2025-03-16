from flask import Blueprint, render_template, session, url_for, redirect, request, jsonify

bp = Blueprint('landing', __name__, url_prefix='/landing')

@bp.route('/', methods=['GET'])
def page():
    return render_template('landing.html')