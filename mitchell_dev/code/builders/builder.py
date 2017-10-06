from .combo_maker import make_combos
from multiprocessing import Process, Manager
import time
from copy import deepcopy

def build(runtime_vars):
    """Returns list of length runtime_vars['max_wanted_schedules'] containing working schedules"""
    feeder_pool = make_combos(runtime_vars)
    if runtime_vars['debug']:
        print('*** Feeder pool ***')
        print(feeder_pool)
        print('*** End feeder pool ***')

    # to make things easy
    builder_params = runtime_vars['builder_params']
    builder_params['runtime_vars'] = runtime_vars
    manager = Manager()
    schedules = manager.list()
    builder_timeout = runtime_vars['builder_timeout']
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

    #if runtime_vars['debug']:
        # NOTE: this will be printed for each process
    #    print('**** STARTING SCHEDULE FRAME ****')
    #    print(starting_frame)
    #    print('**** END ****')

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
                    problems[key] = box_units - box_spread_size # units needing to be moved
        if len(problems) > 0:
            return problems
        else:
            return None  # useless, but for my sanity

    def move_courses_to_next_percent_or_cloud(boxes, bad):
        if 'missing_units' in bad:
            for value2 in bad['missing_units']:
                    boxes['cloud'].append(value2) # put in cloud
                    # remove course from boxes season if in it
                    for season in boxes:
                        if season != 'cloud':
                            if value2 in boxes[season]['courses']:
                                del boxes[season]['courses'][boxes[season]['courses'].index(value2)]

        for season, units in bad.items():
            if season != 'missing_units':
                units_moved = 0
                sort_by_lowest_priority = sorted(boxes[season]['courses'], key=lambda x1: x1.user_priority)
                index = 0
                while units_moved < units:
                    if index >= len(sort_by_lowest_priority):
                        exit()  # exit thread if index out of bounds
                    if sort_by_lowest_priority[index] not in boxes['cloud']:  # to prevent double dipping
                        current_percent = sort_by_lowest_priority[index].percent_chance_offered[season]
                        max_season = None
                        max_percent = None
                        for season1, percent in sort_by_lowest_priority[index].percent_chance_offered.items():
                            if percent < current_percent and percent > 60: # TODO: check consistency -- not .6
                                if max_season is None:
                                    max_season = season1
                                    max_percent = percent
                                else:
                                    if percent > max_percent:
                                        max_percent = percent
                                        max_season = season1
                                # NOTE: assumes coreq will follow whatever it's coreqs % is regardless of reported %,
                                # ex: MATH 3A is 90% and MATH 3AL is 2% and they are coreqs, MATH3AL is then considered to have 90%
                        move_to_season = max_season
                        if move_to_season is None:
                            # move to cloud
                            units_moved += int(sort_by_lowest_priority[index].variables['units'])
                            # remove course from season box
                            del boxes[season]['courses'][boxes[season]['courses'].index(sort_by_lowest_priority[index])]
                            moved = []
                            # go through coreqs
                            for course in boxes[season]['courses']:
                                if course in sort_by_lowest_priority[index].coreq_list:
                                    boxes['cloud'].append(course)
                                    units_moved += int(course.variables['units'])
                                    moved.append(course)
                            for x in moved:
                                del boxes[season]['courses'][boxes[season]['courses'].index(x)]
                        else: # move to new season
                            boxes[move_to_season]['courses'].append(sort_by_lowest_priority[index])
                            units_moved += int(sort_by_lowest_priority[index].variables['units'])
                            del boxes[season]['courses'][boxes[season]['courses'].index(sort_by_lowest_priority[index])]
                            # remove course and coreqs from season box
                            moved = []
                            # go through coreqs
                            for course in boxes[season]['courses']:
                                if course in sort_by_lowest_priority[index].coreq_list:
                                    boxes[move_to_season].append(course)
                                    units_moved += int(course.variables['units'])
                                    moved.append(course)
                            for x in moved:
                                del boxes[season]['courses'][boxes[season]['courses'].index(x)]
                    index += 1

    def sort_courses(boxes, starting_frame, builder_params, courses):
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
                                for x in course.coreq_list:
                                    course_and_coreq_units += int(x.variables['units'])
                                wait_to_place = False
                                for x_name in unplaced_courses:
                                    name_list = [i.course_name for i in courses]
                                    if x_name in name_list:
                                        index = name_list.index(x_name)
                                        for y in courses[index].is_prereq_for:
                                            if y.course_name == course.course_name:
                                                wait_to_place = True
                                    # check if student not upper div (at this point in schedule) and course is upper div only
                                    if 'upper_div_only' in course.variables:
                                        if not builder_params['runtime_vars']['upper_div_student']:
                                            user_units = builder_params['runtime_vars']['units_completed']
                                            num_units_for_upper_div = builder_params['runtime_vars']['units_completed']
                                            units_in_schedule = 0
                                            for key1 in boxes:
                                                if key1 != 'cloud':
                                                    for c in boxes[key1]['courses']:
                                                        if 'units' in c.variables:
                                                            units_in_schedule += int(c.variables['units'])
                                            if user_units + units_in_schedule < num_units_for_upper_div:
                                                wait_to_place = True
                                if new_frame[year][key]['units_used'] + course_and_coreq_units + \
                                       new_frame[year][key]['blacked_out'] > new_frame[year][key]['max_units']:
                                    wait_to_place = True
                                if not wait_to_place:
                                    new_frame[year][key]['courses'][course.course_name] = course
                                    for x in course.coreq_list:
                                        new_frame[year][key]['courses'][x.course_name] = x
                                        if x.course_name in unplaced_courses:
                                            del unplaced_courses[unplaced_courses.index(x.course_name)]
                                    new_frame[year][key]['units_used'] += course_and_coreq_units
                                    if course.course_name in unplaced_courses:
                                        del unplaced_courses[unplaced_courses.index(course.course_name)]
        season_units_dict = {}
        if len(unplaced_courses) > 0:
            for x in unplaced_courses:
                for season in boxes:
                    if season != 'cloud':
                        box_season_names = [i.course_name for i in boxes[season]['courses']]
                        if x in box_season_names:
                            if season not in season_units_dict:
                                season_units_dict[season] = 0
                            unplaced_course = boxes[season]['courses'][box_season_names.index(x)]
                            season_units_dict[season] += int(unplaced_course.variables['units'])
                            for x in unplaced_course.coreq_list:
                                season_units_dict[season] += int(x.variables['units']) # part of moving coreqs together
        if len(season_units_dict) > 0:
            overflow = season_units_dict
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
            if overflow is not None:
                A(boxes, overflow, schedules, timeout, builder_params, courses)
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
        if max_chance[1] < runtime_vars['min_percent_for_scheduling']:
            boxes['cloud'].append(course)
        else: # put course where it is most likely offered
            boxes[max_chance[0]]['courses'].append(course)
    # recursive call
    A(boxes, None, schedules, timeout, builder_params, input)

