import os
import sqlite3

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()
DATABASE = 'mercyhurst_courses.db'
PAGE_TITLE = '📚 Mercyhurst to The Real World 💰'
PAGE_SUBTITLE = 'Click a program to view its degree type, minor status, and salary.'

templates = Jinja2Templates(directory='templates')


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    conn = get_db_connection()
    programs = conn.execute('SELECT id, title FROM courses ORDER BY title').fetchall()
    conn.close()
    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
            'programs': programs,
            'title': PAGE_TITLE,
            'subtitle': PAGE_SUBTITLE,
        },
    )


@app.get('/program/{program_id}', response_class=HTMLResponse)
async def program_detail(request: Request, program_id: int):
    conn = get_db_connection()
    program = conn.execute(
        'SELECT c.id, c.title, c.degree_type, c.minor, s.average_salary, s.source_degree '
        'FROM courses c LEFT JOIN salaries s ON c.id = s.id '
        'WHERE c.id = ?',
        (program_id,),
    ).fetchone()
    conn.close()

    if program is None:
        raise HTTPException(status_code=404, detail='Program not found')

    minor_value = 'yes' if program['minor'] == 'yes' else 'no'
    salary_value = program['average_salary'] if program['average_salary'] else 'N/A'
    source_degree = program['source_degree'] if program['source_degree'] else 'No source available'

    return templates.TemplateResponse(
        'program_detail.html',
        {
            'request': request,
            'program': program,
            'minor_value': minor_value,
            'salary_value': salary_value,
            'source_degree': source_degree,
            'title': PAGE_TITLE,
            'subtitle': PAGE_SUBTITLE,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse('404.html', {'request': request}, status_code=404)
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
