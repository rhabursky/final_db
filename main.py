import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, Session, SQLModel, create_engine, select

app = FastAPI()
DATABASE = 'mercyhurst_courses.db'
engine = create_engine(f'sqlite:///{DATABASE}', echo=False, connect_args={'check_same_thread': False})

app.mount('/static', StaticFiles(directory='static'), name='static')


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


@app.get('/')
async def serve_index():
    return FileResponse('static/index.html')


@app.get('/api/programs')
async def list_programs():
    with get_session() as session:
        programs = session.exec(select(Course).order_by(Course.title)).all()
    return [{'id': program.id, 'title': program.title} for program in programs]


@app.get('/api/programs/{program_id}')
async def get_program(program_id: int):
    with get_session() as session:
        program = session.get(Course, program_id)
        salary = session.get(Salary, program_id)

    if program is None:
        raise HTTPException(status_code=404, detail='Program not found')

    return {
        'id': program.id,
        'title': program.title,
        'degree_type': program.degree_type,
        'minor': program.minor,
        'average_salary': salary.average_salary if salary else None,
        'source_degree': salary.source_degree if salary else None,
    }


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
