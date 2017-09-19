#!/usr/bin/env python 
""" Main handler for Python side
    This will handle all interactions with PhP or the client side.
    For now it simply takes in parameters for making schedules and coordinates building them,
    but later it may do other stuff
"""
from loaders.loader import load
from builders.builder import build
import time

def main():
    """  MOST OF THIS NEEDS TO BE PASSED IN FROM USER SIDE SOMEHOW"""
    runtime_vars = {}
    runtime_vars['debug'] = True

    # CHANGE_VARs -- these are values to adjust performance of schedule building
    runtime_vars['max_feeder_pool_length'] = 200
    runtime_vars['make_fp_iter_count'] = 10000
    runtime_vars['max_options_generated_from_wrapper'] = 100
    runtime_vars['builder_timeout'] = 15 # seconds
    runtime_vars['min_percent_for_scheduling'] = 60 # course must have 60% likelyhood or more in season to be scheduled
                                                    # for that season, otherwise it is put in the cloud
    runtime_vars['max_wanted_schedules'] = 2
    # END CHANGE_VARs

    runtime_vars['institution'] = 'UCI'
    runtime_vars['major'] = 'SOCIOL'
    runtime_vars['BS_BA_Other'] = 'BA'
    runtime_vars['year_declared_under'] ='17-18'
    runtime_vars['specialization'] = None
    runtime_vars['max_user_major_load'] = 18 # most units user is willing to take from major, must not be > max_units allowed by school
    runtime_vars['max_total_user_load'] = 20 # total (for all courses) user is willing to take in a quarter
    runtime_vars['user_has_taken'] = ['SOCIOL 1','SOCIOL 3', 'SOCIOL 110','FAKE CLASS'] # NOTE: This includes what the user is taking
                                                                        # (let's assume the user doesn't fail)
    # TODO -- get quarters/semesters user is taking and store in runtime_vars
    runtime_vars['units_left_for_other_per_user_year'] = 12
    runtime_vars['ap_calc_bc'] = 4 # for testing -- check major.BS file under SSU for supported vars

    course_info, school_vars = load(runtime_vars)
    if runtime_vars['debug']:
        print('\nLength of course_dict: {}\n'.format(len(course_info[2])))
    if course_info is None or school_vars is None:
        print('We do not support this major at this University yet.')
        exit()

    runtime_vars['course_info'] = course_info # has multiple entries: major string, course reqs for major, courses
    runtime_vars['fast_track'] = 0 # 1 or 0
    runtime_vars['preferred_courses'] = None # will impact priorities
    runtime_vars['user_course_vars'] = {'act_math' : 29}
    runtime_vars['upper_div_student'] = 0 # for lower-div or upper_div only classes
    runtime_vars['units_completed'] = 70  # user completed units

    # school vars
    runtime_vars['school_vars'] = school_vars
    runtime_vars['num_units_for_upper_div'] = int(school_vars['min_units_for_upper_div'])
    runtime_vars['min_units_per_quarter'] = int(school_vars['min_units_per_quarter'])
    runtime_vars['total_units_to_graduate'] = int(school_vars['total_units_to_graduate'])
    runtime_vars['credit_measurement'] = school_vars['credit_measurement']
    runtime_vars['semesters_quarters'] = school_vars['semesters_quarters']
    # end school vars

    # TODO: Make add_percents_priorites pull from DB, not randomly generate values
    # add builder_params
    runtime_vars['builder_params'] = {
        # TODO: -- pull this info from above -- hardcoded for now
        # TODO: save spots for electives here, notify user of elective requirements
        # for now things are hardcoded for implementing algorithm
        'start_build_from_year': 2018,
        'start_build_from_season' : 2,
        'seasons': {
            # leave_open_units {2018:4} means leave 4 units open in year 2018 of this quarter
            # seasons are numbered for simplicity 1 == Fall, etc.
            1: {'user_approved': True,
                     'max_units': 20,
                     'leave_open_units': {2018:4, 2019:2},
                     'max_quarters_left': 4
                     },
            2: {'user_approved': True,
                'max_units': 20,
                'leave_open_units': {2018:4, 2019:2},
                'max_quarters_left': 4
                },
            3: {'user_approved': True,
                'max_units': 20,
                'leave_open_units': {2018:4, 2019:2},
                'max_quarters_left': 4
                },
            # if not user_approved, entry need not exist in the first place
            4: {'user_approved': False,
                'max_units': 20,
                'leave_open_units': {2018:4, 2019:2},
                'max_quarters_left': 4
                }
        }
    }

    schedules = build(runtime_vars)

    if runtime_vars['debug']:
        for i,x in enumerate(schedules):
            print('\nSchedule #: {}\n'.format(i + 1))
            for key, value in x.items():
                if key != 'cloud':
                    print('\t{}'.format(key))
                    for season, vars in value.items():
                        print('\t\t{}'.format(season))
                        print('\t\t\t{}'.format(vars))
                else:
                    print('\tCloud\n\t\t{}'.format(value))
        print('\n# schedules produced: {}'.format(len(schedules)))
        print('Time taken: {}'.format(time.time() - start))

    """ WORK FROM HERE """

    """"""""""""""""""""""""
    # TODO pull schedules with least in cloud
    # TODO add class specific info to courses in schedules -- handle level 2
    # TODO get final unit count (total user planned, total user needs)
    # TODO tell user of min units for full time (store in school info)
    # TODO: offer alternative courses for courses in cloud
    # REMEMBER: courses in cloud may have the course they are a prereq for placed in schedule -- be careful

if __name__ == '__main__':
    start = time.time()
    main()

# TODO: make many more .maj files
# TODO: check no duplicates in feeder pool, validity of other schedules

# NOTE: may need one day to possibly account for OR situation with coreqs
    #  -- just use framework vars to make it easy..Only if case comes up