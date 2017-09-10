#!/usr/bin/env python 
""" Main handler for Python side
    This will handle all interactions with PhP or the client side.
    For now it simply takes in parameters for making schedules and coordinates building them,
    but later with flags it may do other stuff
"""
from loaders.loader import load
from builders.builder import build
import time

def main():

    # TODO: when building schedule, check for number of electives user will pick
    	   # and allow numerous slots. Also allow slots for courses outside of major
    # TODO: get variables in some format here
    # TODO: if script exits with anything but desired output to controller (PhP script or another),
    # TODO(cont):"Say, 'Sorry, we do not support this yet.'"
    # TODO: get classes already taken
    # TODO: check all variables when building schedule
    # TODO: write algorithms to step through and build schedule
    # TODO: build in check for if class has a typo -- cross check with course DB
    # TODO: add more .maj files for testing -- final safety is saying we don't support it

    """  MOST OF THIS NEEDS TO BE PASSED IN FROM USER SIDE SOMEHOW"""
    # enter info into dictionary for easy passing...
    runtime_vars = {}
    runtime_vars['institution'] = 'UCI'
    runtime_vars['major'] = 'SOCIOL'
    runtime_vars['BS_BA_Other'] = 'BA'
    runtime_vars['year_declared_under'] ='17-18'
    runtime_vars['specialization'] = None
    runtime_vars['max_user_major_load'] = 18 # most units user is willing to take from major, must not be > max_units allowed by school
    runtime_vars['max_total_user_load'] = 20 # total (for all courses) user is willing to take in a quarter
    runtime_vars['user_has_taken'] = ['SOCIOL 1','SOCIOL 3', 'SOCIOL 110','FAKE CLASS'] # NOTE: This includes what the user is taking
                                                                        # (let's assume the user doesn't fail)
    runtime_vars['quarters_semesters'] = ['quarter', ['F','W','Sp','Su']]
    runtime_vars['units_left_for_other_per_user_year'] = 12
    runtime_vars['max_wanted_schedules'] = 5
    runtime_vars['debug'] = True
    runtime_vars['ap_calc_bc'] = 4 # for testing

    course_info, school_vars = load(runtime_vars)
    runtime_vars['course_info'] = course_info
    runtime_vars['school_vars'] = school_vars
    runtime_vars['fast_track'] = 1 # 1 or 0
    runtime_vars['prefered_courses'] = None # TODO: implement
    runtime_vars['user_course_vars'] = {'act_math' : 29}
    runtime_vars['upper_div_student'] = 0 # for lower-div or upper_div only classes

    if course_info is None or school_vars is None:
        print('We do not support this major at this University yet.')
        exit()

    schedules = build(runtime_vars)

    if runtime_vars['debug']:
        print('\nTime taken: {}'.format(time.time() - start))

if __name__ == '__main__':
    start = time.time()
    main()
