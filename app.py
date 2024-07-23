import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATABASE = {
    'dbname': 'running_tracker',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost'
}


def get_db_connection():
    conn = psycopg2.connect(**DATABASE)
    return conn


def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS runs
                         (id SERIAL PRIMARY KEY, date DATE, distance REAL, notes TEXT)''')
        conn.commit()


init_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add', methods=['GET', 'POST'])
def add_run():
    if request.method == 'POST':
        date = request.form['date']
        distance = request.form['distance']
        notes = request.form.get('notes')
        with get_db_connection() as conn:
            with conn.cursor() as c:
                c.execute('INSERT INTO runs (date, distance, notes) VALUES (%s, %s, %s)',
                          (date, distance, notes))
                conn.commit()
        return redirect(url_for('index'))
    return render_template('add_run.html')


@app.route('/statistics')
def statistics():
    with get_db_connection() as conn:
        with conn.cursor() as c:
            c.execute('SELECT date, distance FROM runs ORDER BY date')
            runs = c.fetchall()
            c.execute('SELECT SUM(distance) FROM runs')
            total_distance = c.fetchone()[0]
    if total_distance is None:
        total_distance = 0.0
    total_distance = round(total_distance, 2)
    return render_template('statistics.html', runs=runs, total_distance=total_distance)


@app.route('/reset', methods=['POST'])
def reset():
    with get_db_connection() as conn:
        with conn.cursor() as c:
            c.execute('DELETE FROM runs')
            conn.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
