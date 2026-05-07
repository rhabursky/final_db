#!/usr/bin/env python3
"""Initialize the database with proper SQLModel tables and import data from SQL file."""
import sqlite3
import os
from pathlib import Path
from typing import Optional

# Get paths
BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / 'mercyhurst_courses.db'
SQL_FILE = BASE_DIR / 'mercyhurst_courses.sql'

# Import SQLModel classes
from sqlmodel import Field, Session, SQLModel, create_engine, select

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

# Remove existing database
if DATABASE_PATH.exists():
    DATABASE_PATH.unlink()
    print("Removed existing database")

# Create engine and tables
engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=False, connect_args={'check_same_thread': False})
SQLModel.metadata.create_all(engine)
print("Created database tables with SQLModel")

# Read SQL file and extract course data
courses_data = []
if SQL_FILE.exists():
    with open(SQL_FILE, 'r') as f:
        sql_content = f.read()
    
    # Extract INSERT statements
    lines = sql_content.split('\n')
    for line in lines:
        if line.startswith("INSERT INTO courses"):
            # Parse the VALUES clause
            # Format: INSERT INTO courses (title, degree_type) VALUES ('Title', 'Type');
            match_start = line.find("VALUES (") + 8
            match_end = line.rfind(");")
            if match_start > 7 and match_end > 0:
                values_str = line[match_start:match_end]
                # Simple CSV parsing (handle escaped quotes)
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
                    # Check if degree_type includes "Minor"
                    has_minor = "Minor" in degree_type
                    courses_data.append((title, degree_type, 'yes' if has_minor else 'no'))

# Insert data
with Session(engine) as session:
    for title, degree_type, minor in courses_data:
        course = Course(title=title, degree_type=degree_type, minor=minor)
        session.add(course)
    session.commit()
    print(f"Inserted {len(courses_data)} courses")

# Verify
with Session(engine) as session:
    count = len(session.exec(select(Course)).all())
    print(f"Database now contains {count} courses")
