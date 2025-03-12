from flask import Blueprint, render_template, session
from lexloop.auth import login_required
from lexloop.db import get_db

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/', methods=['GET'])
@login_required
def display():
    user_id = session.get('user_id')
    db = get_db()

    words = db.execute('''
        SELECT french_word, english_word
        FROM dashboard dash 
        JOIN dictionary dict ON dash.dictionary_id = dict.id
        WHERE dash.user_id = ?
    ''', (user_id,)).fetchall()

    return render_template('dashboard/dashboard.html', words=words)
