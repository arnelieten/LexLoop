from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app
from werkzeug.security import generate_password_hash
import secrets
import datetime
from flask_mail import Mail, Message
from lexloop.db import get_db

bp = Blueprint('reset', __name__, url_prefix='/reset')

mail = Mail()

def init_app(app):
    mail.init_app(app)

def generate_reset_token():
    return secrets.token_urlsafe(32)

def get_expiration_time():
    return datetime.datetime.now() + datetime.timedelta(hours=24)

@bp.route('/request', methods=('GET', 'POST'))
def request_reset():
    if request.method == 'POST':
        email = request.form['email']
        db = get_db()
        error = None
        
        if not email:
            error = 'Email is required.'
        
        user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
        
        if user is None:
            flash('If your email exists in our system, you will receive a password reset link.')
            return redirect(url_for('auth.login'))
            
        if error is None:
            token = generate_reset_token()
            expiration = get_expiration_time()
            
            db.execute(
                'INSERT INTO password_reset (user_id, token, expires_at) VALUES (?, ?, ?)',
                (user['id'], token, expiration)
            )
            db.commit()
            
            reset_url = url_for('reset.reset_password', token=token, _external=True)

            msg = Message('Reset Your LexLoop Password',
                         recipients=[email])
            msg.body = f'''To reset your password, visit the following link:

{reset_url}

This link will expire in 24 hours.

If you did not request a password reset, please ignore this email.
'''
            mail.send(msg)
            
            flash('If your email exists in our system, you will receive a password reset link.')
            return redirect(url_for('auth.login'))
        
        flash(error)
        
    return render_template('auth/password_request.html')

@bp.route('/password/<token>', methods=('GET', 'POST'))
def reset_password(token):
    db = get_db()
    reset_info = db.execute(
        'SELECT user_id, expires_at, used FROM password_reset WHERE token = ?',
        (token,)
    ).fetchone()

    if reset_info is None or reset_info['used'] == 1:
        flash('Invalid or expired password reset link.')
        return redirect(url_for('auth.login'))
    
    now = datetime.datetime.now()
    expires_at = reset_info['expires_at']
    if now > expires_at:
        flash('Password reset link has expired.')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form['password']
        password_check = request.form['password_check']
        error = None
        
        if not password:
            error = 'Password is required.'
        elif password != password_check:
            error = 'Passwords need to match.'
            
        if error is None:
            db.execute(
                'UPDATE user SET password = ? WHERE id = ?',
                (generate_password_hash(password), reset_info['user_id'])
            )
            db.execute(
                'UPDATE password_reset SET used = 1 WHERE token = ?',
                (token,)
            )
            db.commit()
            
            flash('Your password has been reset. You can now log in with your new password.')
            return redirect(url_for('auth.login'))
            
        flash(error)
        
    return render_template('auth/password_reset.html')