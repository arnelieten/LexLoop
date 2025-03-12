import os
import fitz
import spacy
import re
from transformers import pipeline
from flask import Blueprint, request, session, flash, redirect, url_for, send_from_directory, current_app, render_template
from lexloop.auth import login_required
from lexloop.db import get_db

bp = Blueprint('process', __name__, url_prefix='/process')

@bp.route('/<filename>', methods=['GET'])
@login_required
def process_file(filename):
    user_id = session.get('user_id')
    if not user_id:
        flash("User not authenticated!")
        return redirect(url_for('auth.login'))

    file_path = os.path.join(current_app.config['UPLOADS'], filename)

    if not os.path.exists(file_path):
        flash('File not found!')
        return redirect(url_for('uploads.upload_file'))

    ### Change to full document!!!!
    doc = fitz.open(file_path)
    page = doc[0]
    text = page.get_text()


    text = re.sub(r'https?://\S+', '', text)  # URLs
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)  # Emails
    text = re.sub(r'-\s*\n', '', text)  # Hyphens
    text = re.sub(r"[^a-zA-ZÀ-ÖØ-öø-ÿ\s']", '', text)  # Non-alphabetic


    nlp = spacy.load('fr_core_news_md')
    list_french = list(dict.fromkeys([token.lemma_ for token in nlp(text)]))
    list_french = [word.lower() for word in list_french]


    translation_pipeline = pipeline('translation_fr_to_en', model='Helsinki-NLP/opus-mt-tc-big-fr-en')
    list_english = [translation_pipeline(word, return_text=True)[0]['translation_text'] for word in list_french]


    initial_dictionary = dict(zip(list_french, list_english))

    list_dictionary = {
        french.lower(): english.lower()
        for french, english in initial_dictionary.items()
        if french.strip() and english.strip()
        and len(french) >= 5 
        and french.lower() != english.lower()
    }

    db = get_db()

    for french_word, english_word in list_dictionary.items():
        cursor = db.execute("SELECT id FROM dictionary WHERE french_word = ?", (french_word,))
        row = cursor.fetchone()

        if row:
            dictionary_id = row["id"]
        else:
            cursor = db.execute('''
                INSERT INTO dictionary (french_word, english_word)
                VALUES (?, ?)
            ''', (french_word, english_word))
            db.commit()
            dictionary_id = cursor.lastrowid

        db.execute('''
            INSERT OR IGNORE INTO dashboard (user_id, dictionary_id, status_word, switch_date)
            VALUES (?, ?, 'new', NULL)
        ''', (user_id, dictionary_id))

    db.commit()

    words = db.execute('''
        SELECT french_word, english_word
        FROM dashboard dash JOIN dictionary dict ON dash.dictionary_id = dict.id
        WHERE dash.user_id = ?
        ''', (user_id,)).fetchall()

    return render_template('dashboard/dashboard.html', words=words)