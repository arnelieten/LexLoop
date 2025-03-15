from flask import Blueprint, render_template, session, flash, request, redirect, url_for, g
from werkzeug.security import check_password_hash
from lexloop.auth import login_required
from lexloop.db import get_db

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/', methods=['GET'])
@login_required
def settings():
    current_user = session.get('user_id')
    db = get_db()

    counts = db.execute("""
        SELECT status_word, COUNT(*) AS count
        FROM dashboard
        WHERE user_id = ?
        GROUP BY status_word
    """, (current_user,)).fetchall()

    status_counts = {
        'new': 0,
        'known': 0,
        'unknown': 0
    }

    for row in counts:
        status_word = row['status_word']
        if status_word in status_counts:
            status_counts[status_word] = row['count']

    total_words = sum(status_counts.values())

    return render_template('dashboard/profile.html', status_counts=status_counts, total_words=total_words)


@bp.route('/delete_account', methods=('GET', 'POST'))
@login_required
def delete_account():
    if request.method == 'POST':
        password = request.form['password']
        db = get_db()
        error = None
        
        if not check_password_hash(g.user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            try:
                db.execute('DELETE FROM user WHERE id = ?', (g.user['id'],))
                db.commit()
                
                session.clear()
                return redirect(url_for('auth.goodbye'))
            except Exception as e:
                error = f"Error deleting account: {e}"
        
        flash(error)
    
    return render_template('auth/delete.html')