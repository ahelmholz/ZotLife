from .combo_maker import make_combos
from multiprocessing import Process, Manager
import time

# TODO: possibly account for OR situation with coreqs? -- just use framework vars to avoid disaster..Only if case comes up

def build(runtime_vars):
    """Returns list of length runtime_vars['max_wanted_schedules'] containing working schedules"""
    feeder_pool = make_combos(runtime_vars)
    if runtime_vars['debug']:
        print('*** Feeder pool ***')
        print(feeder_pool)
        print('*** End feeder pool ***')

    # to make things easy
    builder_params = {
        # TODO: change -- pull from runtime_vars/user
        # for now things are hardcoded for implementing algorithm
        'start_build_from_year': 2018,
        'start_build_from_season' : 2,
        'seasons': {
            # leave_open_units {2018:4} means leave 4 units open in year 2018 of this quarter
            # seasons are numbered for simplicity
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
            4: {'user_approved': False,
                'max_units': 20,
                'leave_open_units': {2018:4, 2019:2},
                'max_quarters_left': 4
                }
        }
    }
    manager = Manager()
    schedules = manager.list()
    builder_timeout = 30 # CHANGE_VAR -- seconds
    start = time.time()
    i = 0
    while time.time() - start < builder_timeout and len(schedules) < runtime_vars['max_wanted_schedules'] and \
                    i < len(feeder_pool):
        p1 = Process(target=build_schedules, args=(feeder_pool[i], schedules, builder_params, runtime_vars, builder_timeout,))
        if i + 1 < len(feeder_pool):
            p2 = Process(target=build_schedules, args=(feeder_pool[i +1], schedules, builder_params, runtime_vars, builder_timeout,))
        p1.start()
        if i + 1 < len(feeder_pool):
            p2.start()
        p1.join()
        if i + 1 < len(feeder_pool):
            p2.join()
        i += 2
    return schedules
    # AFTER working schedules are built, pool info for those courses from DB for level 2 sorting
    # NOTE:
        # level 1: Courses
        # level 2: Individual classes/labs/discussions
    # TODO: add option to move courses back in case user doesn't pass a course (functionality may be somewhere else)
def add_blackouts(entry, year, blackouts):
    temp = 0
    if year in blackouts:
        temp = blackouts[year]
    entry['blacked_out'] = temp

def build_schedules(input, schedules, builder_params, runtime_vars, timeout):
    start = time.time()
    starting_frame = {}
    max_left = 0
    start_year = builder_params['start_build_from_year']
    start_season = builder_params['start_build_from_season']
    # get max years
    for key in builder_params['seasons']:
        if builder_params['seasons'][key]['max_quarters_left'] > max_left:
            max_left = builder_params['seasons'][key]['max_quarters_left']
    for i in range(max_left):
        starting_frame[start_year + i] = {}
    for season in builder_params['seasons']:
        max_units = builder_params['seasons'][season]['max_units']
        if builder_params['seasons'][season]['user_approved']:
            for year in starting_frame:
                if year == start_year:
                    if season >= start_season:
                        starting_frame[year][season] = {'max_units': max_units, 'units_used': 0, 'courses': {}}
                        add_blackouts(starting_frame[year][season], year,
                                      builder_params['seasons'][season]['leave_open_units'])
                else:
                    starting_frame[year][season] = {'max_units': max_units, 'units_used': 0, 'courses': {}}
                    add_blackouts(starting_frame[year][season], year, builder_params['seasons'][season]['leave_open_units'])

    if runtime_vars['debug']:
        # NOTE: this will be printed for each process
        print('**** STARTING SCHEDULE FRAME ****')
        print(starting_frame)
        print('**** END ****')

    def check_params(builder_params, starting_frame):
        return True # TODO implement

    def recur_build(sorted_courses, index, schedules, starting_frame, builder_params, timeout, start, cloud, placement,
                    course_year_season):
        index += 1
        if not check_params(builder_params, starting_frame): # bad schedule
            return
        if index == len(sorted_courses):
            print('Base case reached')
            #schedules.append([starting_frame, cloud])
            return
        for course in sorted_courses[index:]:  # start with highest priority down to smallest
            if time.time() - start < timeout and len(schedules) < runtime_vars['max_wanted_schedules']:
                if not placement[course]:
                    percent_high_to_low = sorted(list(course.percent_chance_offered.items()), key=lambda x: x[1],
                                                 reverse=True)
                    for season_chance in percent_high_to_low:
                        if season_chance[1] < 30:  # < 30%
                            cloud.append(course)
                        else:
                            # TODO: implement here
                            # if course has prereqs, place prereqs earliest, course with coreqs together at soonest possible
                            #   after prereqs
                            # make prereq placement for course and coreqs recursive -- only use prereqs/coreqs
                            # else place course in nearest year
                            # adjust all data structures
                            # check if year/season even exist in starting_frame, if not, move on
                            # units/credits change -- do math with blacklisted/total allowed per quarter in check params




                            recur_build(sorted_courses, index, schedules, starting_frame, builder_params, timeout,
                                        start, cloud, placement, course_year_season)

                            # TODO undo placements in data structures
                            # placement[course]
                            # course_year_season
                            # cloud



    cloud = [] # suggest other classes or make user schedule
    index = 0
    sorted_courses = sorted(input, key=lambda x1: x1.user_priority, reverse=True)
    placement = {} # to keep track of what has been placed and what hasn't
    course_year_season = {}
    for course in input:
        placement[course] = False
        course_year_season[course] = [-1, -1]  # not input yet

    # recursive call
    recur_build(sorted_courses, -1, schedules, starting_frame, builder_params, timeout,
                 start, cloud, placement, course_year_season)
    print('HERE')


