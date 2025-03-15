from flask import Blueprint, render_template, session, url_for, redirect, request, jsonify
from lexloop.auth import login_required
from lexloop.db import get_db

bp = Blueprint('flashcards', __name__, url_prefix='/flashcards')

@bp.route('/', methods=['GET'])
@login_required
def display():
    current_user = session.get('user_id')
    db = get_db()
    
    words = db.execute('''
        SELECT dict.id, dict.french_word, dict.english_word
        FROM dashboard dash
        JOIN dictionary dict ON dash.dictionary_id = dict.id
        WHERE dash.user_id = ? AND dash.status_word = 'unknown'
    ''', (current_user,)).fetchall()
    
    if not words:
        return render_template('dashboard/empty.html')
    
    return render_template('dashboard/flashcards.html', words=words)


@bp.route('/mark-known/<int:word_id>', methods=['POST'])
@login_required
def mark_known(word_id):
    current_user = session.get('user_id')
    db = get_db()
    
    db.execute('''
        UPDATE dashboard
        SET status_word = 'known'
        WHERE user_id = ? AND dictionary_id = ?
    ''', (current_user, word_id))
    db.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success'})
    
    return redirect(url_for('flashcards.display'))

@bp.route('/next/<int:current_index>/<int:total>', methods=['GET'])
@login_required
def next_card(current_index, total):
    next_index = (current_index + 1) % total if total > 0 else 0
    return jsonify({'next_index': next_index})

@bp.route('/prev/<int:current_index>/<int:total>', methods=['GET'])
@login_required
def prev_card(current_index, total):
    prev_index = (current_index - 1) % total if total > 0 else 0
    return jsonify({'prev_index': prev_index})