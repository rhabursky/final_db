from flask import Flask, render_template, abort
import sqlite3

app = Flask(__name__)
DATABASE = 'mercyhurst_courses.db'
PAGE_TITLE = '📚 Mercyhurst to The Real World 💰'
PAGE_SUBTITLE = 'Click a program to view its degree type, minor status, and salary.'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    programs = conn.execute('SELECT id, title FROM courses ORDER BY title').fetchall()
    conn.close()
    return render_template(
        'index.html',
        programs=programs,
        title=PAGE_TITLE,
        subtitle=PAGE_SUBTITLE
    )


@app.route('/program/<int:program_id>')
def program_detail(program_id):
    conn = get_db_connection()
    program = conn.execute(
        'SELECT c.id, c.title, c.degree_type, c.minor, s.average_salary, s.source_degree '
        'FROM courses c LEFT JOIN salaries s ON c.id = s.id '
        'WHERE c.id = ?', (program_id,)
    ).fetchone()
    conn.close()
    if program is None:
        abort(404)

    minor_value = 'yes' if program['minor'] == 'yes' else 'no'
    salary_value = program['average_salary'] if program['average_salary'] else 'N/A'
    source_degree = program['source_degree'] if program['source_degree'] else 'No source available'

    return render_template(
        'program_detail.html',
        program=program,
        minor_value=minor_value,
        salary_value=salary_value,
        source_degree=source_degree,
        title=PAGE_TITLE,
        subtitle=PAGE_SUBTITLE
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
