import os

# Delete mercyhurst_courses_fixed.sql
if os.path.exists('mercyhurst_courses_fixed.sql'):
    os.remove('mercyhurst_courses_fixed.sql')
    print("Deleted mercyhurst_courses_fixed.sql")
else:
    print("File not found")