import os
import web
from django.core.wsgi import get_wsgi_application
from planetterp.config import USER, PASSWORD
import time
# https://stackoverflow.com/a/43391786
os.environ['DJANGO_SETTINGS_MODULE'] = 'planetterp.settings'
application = get_wsgi_application()

db_name = os.environ.get("PLANETTERP_MYSQL_DB_NAME", "planetterp")
db = web.database(dbn='mysql', db=db_name, user=USER, pw=PASSWORD, charset='utf8mb4')

#db.query('DROP TABLE planetterp.views')
#db.query('DROP TABLE planetterp.discussions')
#db.query('DROP TABLE planetterp.fall_2020_searches')
#db.query('DROP TABLE planetterp.replies')
#db.query('DROP TABLE planetterp.groupme_auth')
#db.query('DROP TABLE planetterp.groupme_user_groups')
#db.query('DROP TABLE planetterp.courses_copy')
#db.query('DROP TABLE planetterp.grades2')
#db.query('DROP TABLE planetterp.professor_courses_copy')
#db.query('DROP TABLE planetterp.professors_copy')
#db.query('DROP TABLE planetterp.reviews_copy')
#db.query('DROP TABLE planetterp.organizations_review')

# Handling random things that need to be changed
db.query("UPDATE planetterp.users SET email = NULL WHERE CHARACTER_LENGTH(email) > 254 OR email = ''")
db.query('DELETE FROM planetterp.reviews WHERE professor_id < 0')
db.query('DELETE FROM planetterp.grades WHERE professor_id < 0')
db.query('DELETE FROM planetterp.grades_historical WHERE professor_id < 0')
db.query('DELETE FROM planetterp.professor_courses WHERE professor_id < 0')
db.query('DELETE FROM planetterp.professors WHERE id < 0')

# All reviews with reviewer_id = -1 are updated to reviewer_id = 1. This is a
# temporary solution until the User subclass has been implemented.
db.query('UPDATE planetterp.reviews SET reviewer_id = 1 WHERE reviewer_id = -1')
db.query('DELETE FROM planetterp.users WHERE id = -1')

# Merge professors with duplicate slugs and delete all duplicate professors.
# Only keep the professor that was created first
professors = db.query('SELECT * FROM planetterp.professors WHERE slug IS NOT NULL ORDER BY created DESC')
for professor in professors:
    query = db.query('SELECT id FROM planetterp.professors WHERE slug = $slug ORDER BY created DESC', vars={"slug": professor["slug"]})
    p_ids = [record["id"] for record in query]

    if len(p_ids) > 1:
        kwargs = {
            "new_id": p_ids[-1],
            "curr_id": professor["id"]
        }

        db.query('UPDATE planetterp.reviews SET professor_id = $new_id WHERE professor_id = $curr_id', vars=kwargs)
        db.query('UPDATE planetterp.grades SET professor_id = $new_id WHERE professor_id = $curr_id', vars=kwargs)
        db.query('UPDATE planetterp.grades_historical SET professor_id = $new_id WHERE professor_id = $curr_id', vars=kwargs)
        db.query('UPDATE planetterp.professor_courses SET professor_id = $new_id WHERE professor_id = $curr_id', vars=kwargs)
        db.query('DELETE FROM planetterp.professors WHERE id = $id', vars={"id": professor["id"]})

# Select all historical courses that are NOT in planetterp.courses.
# Inverse join: https://www.sitepoint.com/community/t/how-to-do-an-inverse-join/3224/2
distinct_historical_courses = db.query(
    "SELECT planetterp.courses_historical.id, planetterp.courses_historical.department, planetterp.courses_historical.course_number, planetterp.courses_historical.created FROM planetterp.courses_historical LEFT JOIN planetterp.courses ON planetterp.courses.department = planetterp.courses_historical.department AND planetterp.courses.course_number = planetterp.courses_historical.course_number WHERE planetterp.courses.department IS NULL AND planetterp.courses.course_number IS NULL"
)

max_id = int(db.query('SELECT MAX(id) FROM planetterp.courses')[0]['MAX(id)']) + 1
for idx, course in enumerate(distinct_historical_courses):
    # update the course_id for relevant historical grades so they refer to
    # the right course
    db.query('UPDATE planetterp.grades_historical SET course_id = $new_id WHERE course_id = $curr_id',
        vars={
            "new_id": str(max_id + idx),
            "curr_id": course['id']
        }
    )

    # insert historical courses into planetterp.courses
    db.query(
        'INSERT INTO planetterp.courses (department, course_number, created) VALUES ($department, $course_number, $created)',
        vars={
            "department": course["department"],
            "course_number": course["course_number"],
            "created": course["created"]
        }
    )

# Repeat the above process of updating historic_grades.course_id for the courses
# that already exist in planetterp.courses
historical_courses = db.query(
    'SELECT planetterp.courses_historical.id FROM planetterp.courses_historical LEFT JOIN planetterp.courses ON planetterp.courses.department = planetterp.courses_historical.department AND planetterp.courses.course_number = planetterp.courses_historical.course_number'
)

max_id = int(db.query('SELECT MAX(id) FROM planetterp.courses')[0]['MAX(id)']) + 1
for idx, course in enumerate(historical_courses):
    db.query('UPDATE planetterp.grades_historical SET course_id = $new_id WHERE course_id = $curr_id',
        vars={
            "new_id": str(max_id + idx),
            "curr_id": course['id']
        }
    )

# Move all historical grades to planetterp.grades
grades = db.query('SELECT * FROM planetterp.grades_historical')
for grade in grades:
    db.query(
        'INSERT INTO planetterp.grades (semester, course_id, section, professor_id, num_students, APLUS, A, AMINUS, BPLUS, B, BMINUS, CPLUS, C, CMINUS, DPLUS, D, DMINUS, F, W, OTHER) VALUES ($semester, $course, $professor, $students, $AP, $A, $AM, $BP, $B, $BM, $CP, $C, $CM, $DP, $D, $DM, $F, $W, $OTHER)',
        vars={
            "semester": grade["semester"],
            "course": grade["courde_id"],
            "professor": grade["professor_id"],
            "students": grade["num_students"],
            "AP": grade["APLUS"],
            "A": grade["A"],
            "AM": grade["AMINUS"],
            "BP": grade["BPLUS"],
            "B": grade["B"],
            "BM": grade["BMINUS"],
            "CP": grade["CPLUS"],
            "C": grade["C"],
            "CM": grade["CMINUS"],
            "DP": grade["DPLUS"],
            "D": grade["D"],
            "DM": grade["DMINUS"],
            "F": grade["F"],
            "W": grade["W"],
            "OTHER": grade["OTHER"]
        }
    )
