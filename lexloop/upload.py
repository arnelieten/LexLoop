import os
from flask import Flask, flash, request, redirect, url_for, Blueprint, current_app, render_template, send_from_directory
from werkzeug.utils import secure_filename
from lexloop.auth import login_required


bp = Blueprint('uploads', __name__, url_prefix='/uploads')

allowed_extensions = {'txt', 'pdf', '.docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@bp.route('/', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOADS'], filename))
            flash('File uploaded successfully!')
            return redirect(url_for('process.process_file', filename=filename))
    return render_template('uploads/uploads.html')