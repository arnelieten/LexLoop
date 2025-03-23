from flask import Blueprint, render_template

bp = Blueprint('landing', __name__, url_prefix='/landing')

@bp.route('/', methods=['GET'])
def page():
    return render_template('landing.html')