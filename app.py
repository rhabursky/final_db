import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Field, Session, SQLModel, create_engine, select
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()
DATABASE = 'mercyhurst_courses.db'
PAGE_TITLE = '📚 Mercyhurst to The Real World 💰'
PAGE_SUBTITLE = 'Click a program to view its degree type, minor status, and salary.'

templates = Jinja2Templates(directory='templates')
engine = create_engine(f'sqlite:///{DATABASE}', echo=False, connect_args={'check_same_thread': False})


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    degree_type: Optional[str] = None
    minor: Optional[str] = None


class Salary(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    average_salary: Optional[str] = None
    source_degree: Optional[str] = None


def get_session() -> Session:
    return Session(engine)


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    with get_session() as session:
        programs = session.exec(select(Course).order_by(Course.title)).all()
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
    with get_session() as session:
        program = session.get(Course, program_id)
        salary = session.get(Salary, program_id)

    if program is None:
        raise HTTPException(status_code=404, detail='Program not found')

    minor_value = 'yes' if program.minor == 'yes' else 'no'
    salary_value = salary.average_salary if salary and salary.average_salary else 'N/A'
    source_degree = salary.source_degree if salary and salary.source_degree else 'No source available'

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
