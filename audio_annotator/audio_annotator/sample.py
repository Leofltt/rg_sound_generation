import os
import io
import pandas as pd

from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file
from audio_annotator import db, auth
from audio_annotator.qualities import qualities, pairs


bp = Blueprint('sample', __name__, url_prefix='/sample')


@bp.route('/stats', methods=['GET', 'POST'])
@auth.login_required
def show_stats():
    database = db.get_db()
    if request.method == 'POST':
        db_df = pd.read_sql_query('SELECT * FROM sample', database)
        csv_stream = io.StringIO()
        db_df.to_csv(csv_stream, index=False)
        byte_stream = io.BytesIO()
        byte_stream.write(csv_stream.getvalue().encode())
        byte_stream.seek(0)
        csv_stream.close()
        return send_file(
            byte_stream,
            as_attachment=True,
            attachment_filename='db.csv',
            mimetype='text/csv'
        )
    query = 'SELECT'
    for q in qualities:
        query += f' SUM(q_{q}),'
    query = query[:-1] + ' FROM sample'
    samples = database.execute(
        query
    ).fetchone()
    counts = dict((qualities[i], s) for i, s in enumerate(samples))
    return render_template('stats.html', counts=counts)


@bp.route('/<int:sample_id>', methods=['GET', 'POST'])
@auth.login_required
def show_sample(sample_id):
    database = db.get_db()
    if request.method == 'POST':
        s = database.execute(
            'SELECT * FROM sample WHERE id = ?',
            (sample_id,)
        ).fetchone()
        if s is None:
            flash('No such file found')
            return render_template('index.html')
        present_qualities = [value for key, value in list(request.form.items()) if key != 'description']
        description = request.form['description']
        values = [int(q in present_qualities) for q in qualities]
        current_values = [s[f'q_{q}'] for q in qualities]
        updated_values = [v + current_values[i] for i, v in enumerate(values)]
        current_description = s['description'] or ''
        updated_description = current_description + f',{description}'
        query = ' = ?, '.join([f'q_{q}' for q in qualities])
        query = 'UPDATE sample SET ' + query + ' = ?, description = ? WHERE id = ?'
        database.execute(
            query,
            updated_values + [updated_description, sample_id]
        )
        database.commit()
        flash('Annotation saved')
        return redirect(url_for('sample.next_sample'))
    s = database.execute(
        'SELECT * FROM sample WHERE id = ?',
        (sample_id, )
    ).fetchone()
    if s is None:
        flash('No such file found')
        return render_template('index.html')
    else:
        file_name = s['file_name']
        image_name = f'{os.path.splitext(file_name)[0]}.png'
        return render_template(
            'sample/show.html',
            file_name=file_name,
            image_name=image_name,
            pairs=[p for p in enumerate(pairs)],
            sample_id=sample_id
        )


@bp.route('/next_sample', methods=['GET'])
def next_sample():
    database = db.get_db()
    sample = database.execute(
        'SELECT * FROM sample ORDER BY RANDOM() LIMIT 1;'
    ).fetchone()
    flash('Loading next sample..')
    return redirect(url_for('sample.show_sample', sample_id=sample['id']))
