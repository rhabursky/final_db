from sqlmodel import Session, create_engine, select
from main import Course, Salary, DATABASE

engine = create_engine(f'sqlite:///{DATABASE}', echo=False, connect_args={'check_same_thread': False})

with Session(engine) as session:
    courses = session.exec(select(Course)).all()
    print(f"Total courses: {len(courses)}")
    if courses:
        print("\nFirst 5 courses:")
        for course in courses[:5]:
            print(f"  - {course.title} (ID: {course.id})")
    else:
        print("No courses found in database!")
    
    salaries = session.exec(select(Salary)).all()
    print(f"\nTotal salaries: {len(salaries)}")
