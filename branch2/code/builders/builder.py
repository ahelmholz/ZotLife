from .combo_maker import make_combos
from multiprocessing import Process, Manager
import time
from copy import deepcopy

# TODO: possibly account for OR situation with coreqs? -- just use framework vars to avoid disaster..Only if case comes up

def build(runtime_vars):
    """Returns list of length runtime_vars['max_wanted_schedules'] containing working schedules"""
    feeder_pool = make_combos(runtime_vars)
    if runtime_vars['debug']:
        print('*** Feeder pool ***')
        print(feeder_pool)
        print('*** End feeder pool ***')

    # new data structure out of feeder_pool...Originally not planned


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
    builder_timeout = 15 # CHANGE_VAR -- seconds
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

    def found_problem_fast(boxes):
        # return all overflowed boxes
        problems = {}
        for key in boxes:
            if key != 'cloud':
                box = boxes[key]
                box_spread_size = box['box_spread_size']
                box_units = 0
                for course in box['courses']:
                    if 'units' not in course.variables:
                        if 'missing_units' not in problems:
                            problems['missing_units'] = []
                        problems['missing_units'].append(course) # courses needing to be added to cloud
                    else:
                        box_units += int(course.variables['units'])
                if box_units > box_spread_size:
                    problems[key] = box_spread_size - box_units # units needing to be moved
        if len(problems) > 0:
            return problems
        else:
            return None # useless, but for my sanity

    # check keys, missing units, overflow_years
    def move_courses_to_next_percent_or_cloud(boxes, bad):
        pass # TODO implement, if coreq moved, move course

    def sort_courses(boxes, starting_frame, builder_params, courses):
        # TODO: check upper div
        new_frame = deepcopy(starting_frame)
        new_frame['cloud'] = boxes['cloud'] # add cloud
        overflow = None
        unplaced_courses = [course.course_name for course in courses if course not in boxes['cloud']]
        for i in range(len(starting_frame)):
            year = i + builder_params['start_build_from_year']
            for key in boxes:
                if key != 'cloud':
                    if key in new_frame[year]:
                        for course in boxes[key]['courses']:
                            if course.course_name in unplaced_courses:
                                course_units = int(course.variables['units'])
                                course_and_coreq_units = course_units
                                course_and_coreq_prereqs = course.prereqs
                                for x in course.coreq_list:
                                    course_and_coreq_prereqs += x.prereqs
                                    course_and_coreq_units += int(x.variables['units'])
                                wait_to_place = False
                                for prereq in course_and_coreq_prereqs:
                                    # if prereq in unplaced, don't place
                                    # TODO figure out how to check this
                                    pass
                                if new_frame[year][key]['units_used'] + course_and_coreq_units + \
                                       new_frame[year][key]['blacked_out'] > new_frame[year][key]['max_units']:
                                    wait_to_place = True
                                if not wait_to_place:
                                    # place course and course coreqs
                                    # add to units_used, remove name from unplaced_courses
                                    # TODO update here
                                    pass
        # TODO if unplaced_courses not empty, there is overflow

        return new_frame, overflow # this overflow is years, list of lists [season, course]

    def A(boxes, bad, schedules, timeout, builder_params, courses): # a great function name if I do say so myself
        if time.time() - start > timeout or len(schedules) >= runtime_vars['max_wanted_schedules']:
            return
        if bad is not None:
            move_courses_to_next_percent_or_cloud(boxes, bad)
        problems = found_problem_fast(boxes)
        if problems is not None:
            A(boxes, problems, schedules, timeout, builder_params, courses)
        else:
            new_frame, overflow = sort_courses(boxes, starting_frame, builder_params, courses)
            problems_2 = None
            if overflow is not None:
                problems_2['overflow_years'] = overflow
            if problems_2 is not None:
                A(boxes, problems_2, schedules, timeout, builder_params, courses)
            else:
                schedules.append(new_frame)

    boxes = {}
    for season in builder_params['seasons']:
        if builder_params['seasons'][season]['user_approved']:
            box_spread_size = 0
            for year in starting_frame:
                if season in starting_frame[year]:
                    box_spread_size += starting_frame[year][season]['max_units'] - \
                                       starting_frame[year][season]['blacked_out']
            boxes[season] = {'box_spread_size': box_spread_size, 'courses': []}
    boxes['cloud'] = []
    # attempt build with highest percentages first
    for course in input:
        max_chance = [0, 0] # season, chance
        for season in course.percent_chance_offered:
            if course.percent_chance_offered[season] > max_chance[1]:
                max_chance[0] = season
                max_chance[1] = course.percent_chance_offered[season]
        if max_chance[1] < 60: # CHANGE_VAR
            boxes['cloud'].append(course)
        else: # put course where it is most likely offered
            boxes[max_chance[0]]['courses'].append(course)
    # recursive call
    A(boxes, None, schedules, timeout, builder_params, input)

