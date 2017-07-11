
# kind of pseudocode

# for now, everything loaded (per major) and processed during runtime. TODO: optimize whole process later

# all courses move through these until remaining in finished_courses
# much of this may be in a database instead of in runtime lists

# courses unable to be taken yet because they are not offered in this quarter or have unmet prereqs
future_courses = []

# courses able to be picked from for the upcoming quarter
potential_courses = []

# courses taken or being taken by the user
# when a class is moved here, if it is a prereq, the following course (in future_courses)
#     is checked for other unsatisfied prereqs, and if there are none, it is moved to potential_courses
# TODO: add option to move courses back in case user doesn't pass a course
past_courses = []





