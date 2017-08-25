#!/usr/bin/env python 
""" Main handler for Python side
    This will handle all interactions with PhP or the client side.
    For now it simply takes in parameters for making schedules and coordinates building them,
    but later with flags it may do other stuff
"""
from loaders.loader import load
from loaders.Course import Course

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

    institution = 'UCI'
    major = 'SOCIOL'
    BS_BA_Other = 'BA'
    year_declared_under ='17-18'
    specialization = None
    max_user_major_load = 18 # most units user is willing to take from major, must not be > max_units allowed by school
    course_info, school_vars = load(institution, major, BS_BA_Other, year_declared_under, specialization, debug=True)
    if course_info is None or school_vars is None:
        print('We do not support this major at this University yet.')
        exit()

if __name__ == '__main__':
    main()
