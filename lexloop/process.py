import os
import fitz  # PyMuPDF
import spacy
import re
import pandas as pd
from transformers import pipeline
from flask import Blueprint, request, flash, redirect, url_for, send_from_directory, current_app
from lexloop.auth import login_required

bp = Blueprint('process', __name__, url_prefix='/process')

@bp.route('/<filename>', methods=['GET'])
@login_required
def process_file(filename):
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

    #dataframe best solution here? do not use!
    df = pd.DataFrame({"French": list_french, "English": list_english})
    df = df[(df['French'] != df['English']) & (df['French'].str.len() >= 3)]
    df = df.dropna().replace('', float('nan')).dropna()
    df = df.sample(frac=1)

    # create way to store in databases!
    excel_path = os.path.join(current_app.config['UPLOADS'], f"{filename}.xlsx")
    df.to_excel(excel_path, index=False)

    flash(f'Processing complete! Download your file: {filename}.xlsx')
    return send_from_directory(current_app.config['UPLOADS'], f"{filename}.xlsx", as_attachment=True)
