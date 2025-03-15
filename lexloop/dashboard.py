from flask import Blueprint, render_template, session, url_for, redirect
from lexloop.auth import login_required
from lexloop.db import get_db

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/', methods=['GET'])
@login_required
def display():
    current_user = session.get('user_id')
    db = get_db()

    words = db.execute('''
        SELECT french_word, english_word, dash.dictionary_id
        FROM dashboard dash 
        JOIN dictionary dict ON dash.dictionary_id = dict.id
        WHERE dash.user_id = ?
        AND dash.status_word = 'new'
    ''', (current_user,)).fetchall()

    return render_template('dashboard/dashboard.html', words=words)


@bp.route('/known/<int:word_marker>', methods=['POST'])
@login_required
def status_known(word_marker):
    current_user = session.get('user_id')
    db = get_db()

    db.execute('''
    UPDATE dashboard
    SET status_word = 'known'
    WHERE user_id = ?
    AND dictionary_id = ?
    ''', (current_user, word_marker))

    db.commit()

    return redirect(url_for('dashboard.display'))


@bp.route('/unknown/<int:word_marker>', methods=['POST'])
@login_required
def status_unknown(word_marker):
    current_user = session.get('user_id')
    db = get_db()

    db.execute('''
    UPDATE dashboard
    SET status_word = 'unknown'
    WHERE user_id = ?
    AND dictionary_id = ?
    ''', (current_user, word_marker))

    db.commit()

    return redirect(url_for('dashboard.display'))
