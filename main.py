import os
from typing import Optional
from pathlib import Path
import re

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, Session, SQLModel, create_engine, select

app = FastAPI()

# Get absolute paths
BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / 'mercyhurst_courses.db'
SQL_FILE = BASE_DIR / 'mercyhurst_courses.sql'
STATIC_DIR = BASE_DIR / 'static'

engine = create_engine(f'sqlite:///{DATABASE}', echo=False, connect_args={'check_same_thread': False})

app.mount('/static', StaticFiles(directory=str(STATIC_DIR), check_dir=True), name='static')


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


def initialize_database():
    """Initialize database tables and populate with data from SQL file."""
    # Remove existing database to force fresh load
    if DATABASE.exists():
        DATABASE.unlink()
    
    # Create tables
    SQLModel.metadata.create_all(engine)
    
    # Salary data from Payscale
    salaries_data = [
        ('Accounting', '$86k', 'Master of Business Administration (MBA), Accounting'),
        ('Anthropology and Archaeology', '$60k', 'Anthropology'),
        ('Applied Forensic Sciences', '$60k', 'Forensic Science'),
        ('Applied Sociology', '$55k', 'Sociology'),
        ('Art Education', '$50k', 'Education'),
        ('Art Therapy', '$70k', 'Psychology'),
        ('Artificial Intelligence and Data Science', '$110k', 'Data Science'),
        ('Biology', '$75k', 'Biology'),
        ('Business and Competitive Intelligence', '$72k', 'Business Intelligence'),
        ('Business Economics', '$85k', 'Economics'),
        ('Chemistry & Biochemistry', '$80k', 'Chemistry'),
        ('Communication', '$55k', 'Communications'),
        ('Composition (Music)', '$50k', 'Music'),
        ('Criminal Justice', '$50k', 'Criminal Justice'),
        ('Cyber Security', '$126k', 'Cyber Security'),
        ('Dance', '$45k', 'Performing Arts'),
        ('Early Childhood Education | Special Education', '$50k', 'Education'),
        ('Exercise Science', '$50k', 'Kinesiology'),
        ('English', '$55k', 'English'),
        ('Environmental Science', '$65k', 'Environmental Science'),
        ('Fashion Merchandising', '$50k', 'Fashion Design'),
        ('Finance', '$82k', 'Finance'),
        ('Geology', '$70k', 'Geology'),
        ('Graphic Design', '$55k', 'Graphic Design'),
        ('History', '$60k', 'History'),
        ('Hospitality Management', '$50k', 'Hospitality Management'),
        ('Human Resource Management', '$70k', 'Human Resources'),
        ('Interior Architecture and Design', '$55k', 'Interior Design'),
        ('Intelligence Studies', '$75k', 'International Relations'),
        ('International Business', '$78k', 'International Business'),
        ('Management', '$80k', 'Management'),
        ('Marketing', '$72k', 'Marketing'),
        ('Music Education', '$55k', 'Education'),
        ('Music', '$50k', 'Music'),
        ('Nursing (RN to BSN)', '$77k', 'Nursing'),
        ('Nursing (BSN)', '$77k', 'Nursing'),
        ('Performance (Music)', '$50k', 'Music'),
        ('Physical Therapist Assistant', '$60k', 'Physical Therapy'),
        ('Physics', '$90k', 'Physics'),
        ('Political Science', '$70k', 'Political Science'),
        ('Psychology', '$70k', 'Psychology'),
        ('Pre_Athletic Training', '$50k', 'Sports Medicine'),
        ('Public Health', '$65k', 'Public Health'),
        ('Religious Studies', '$50k', 'Religious Studies'),
        ('Russian Studies', '$55k', 'Foreign Languages'),
        ('Social Work', '$50k', 'Social Work'),
        ('Sport and Event Management', '$50k', 'Sports Management'),
        ('Spanish and Spanish Education', '$55k', 'Spanish'),
        ('Sport Business Management', '$50k', 'Sports Management'),
        ('Sports Medicine', '$50k', 'Sports Medicine'),
        ('Studio Art', '$50k', 'Fine Arts'),
    ]
    
    # Check if data exists
    with Session(engine) as session:
        if len(session.exec(select(Course)).all()) == 0:
            # No data, populate from SQL file
            if SQL_FILE.exists():
                with open(SQL_FILE, 'r') as f:
                    sql_content = f.read()
                
                # Extract INSERT statements
                lines = sql_content.split('\n')
                for line in lines:
                    if line.startswith("INSERT INTO courses"):
                        # Parse the VALUES clause
                        match_start = line.find("VALUES (") + 8
                        match_end = line.rfind(");")
                        if match_start > 7 and match_end > 0:
                            values_str = line[match_start:match_end]
                            # Parse title and degree_type
                            parts = []
                            in_quote = False
                            current = ""
                            for char in values_str:
                                if char == "'" and (not current or current[-1] != '\\'):
                                    in_quote = not in_quote
                                elif char == ',' and not in_quote:
                                    parts.append(current.strip().strip("'").replace("''", "'"))
                                    current = ""
                                    continue
                                current += char
                            if current:
                                parts.append(current.strip().strip("'").replace("''", "'"))
                            
                            if len(parts) == 2:
                                title, degree_type = parts
                                has_minor = "Minor" in degree_type
                                course = Course(
                                    title=title, 
                                    degree_type=degree_type, 
                                    minor='yes' if has_minor else 'no'
                                )
                                session.add(course)
                session.commit()
        
        # Populate salaries
        if len(session.exec(select(Salary)).all()) == 0:
            for title, salary, source in salaries_data:
                salary_record = Salary(
                    title=title,
                    average_salary=salary,
                    source_degree=source
                )
                session.add(salary_record)
            session.commit()


def get_session() -> Session:
    return Session(engine)


@app.get('/', response_class=HTMLResponse)
async def serve_index():
    with open(str(STATIC_DIR / 'index.html'), 'r') as f:
        return f.read()


@app.get('/api/programs')
async def list_programs():
    with get_session() as session:
        programs = session.exec(select(Course).order_by(Course.title)).all()
    return [{'id': program.id, 'title': program.title} for program in programs]


@app.get('/api/programs/{program_id}')
async def get_program(program_id: int):
    with get_session() as session:
        program = session.get(Course, program_id)
        
    if program is None:
        raise HTTPException(status_code=404, detail='Program not found')
    
    # Find salary by matching program title
    with get_session() as session:
        salary = session.exec(select(Salary).where(Salary.title == program.title)).first()

    return {
        'id': program.id,
        'title': program.title,
        'degree_type': program.degree_type,
        'minor': program.minor,
        'average_salary': salary.average_salary if salary else None,
        'source_degree': salary.source_degree if salary else None,
    }


# Initialize database when module is imported/app starts
initialize_database()


def get_port(default: int = 5000) -> int:
    port_value = os.environ.get('PORT', '').strip()
    if not port_value:
        return default
    try:
        return int(port_value)
    except ValueError:
        return default


if __name__ == '__main__':
    import uvicorn

    port = get_port()
    print(f'Starting app on http://0.0.0.0:{port}')
    uvicorn.run(app, host='0.0.0.0', port=port)
