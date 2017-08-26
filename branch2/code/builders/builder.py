def build(runtime_vars):
    # for easy access
    max_units_allowed_per_quarter = int(runtime_vars['school_vars']['max_units'])
    total_units_to_graduate = int(runtime_vars['school_vars']['total_units_to_graduate'])
    max_major_units = int(runtime_vars['max_user_major_load'])
    max_user_total = int(runtime_vars['max_total_user_load'])
    major_req = runtime_vars['course_info'][1]
    courses = runtime_vars['course_info'][2]
    elective_info = runtime_vars['course_info'][3]
    year_time_division = runtime_vars['quarters_semesters'][0]
    seasons = runtime_vars['quarters_semesters'][1]
    num_slots_to_leave_open = runtime_vars['units_left_for_other_per_user_year']
    max_schedules = runtime_vars['max_wanted_schedules']
    do_not_take_dict = {}
    user_has_taken_dict = {}


    # all courses move through these until remaining in finished_courses
    # much of this may be in a database instead of in runtime lists

    # courses unable to be taken yet because they are not offered in this quarter or have unmet prereqs
    future_courses = {}
    # TODO: allow slots for other courses
    # courses able to be picked from for the upcoming quarter
    potential_courses = {}

    # courses taken or being taken by the user
    # when a class is moved here, if it is a prereq, the following course (in future_courses)
    #     is checked for other unsatisfied prereqs, and if there are none, it is moved to potential_courses
    # TODO: add option to move courses back in case user doesn't pass a course
    past_courses = {}



