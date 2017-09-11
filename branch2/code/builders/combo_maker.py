from loaders import CourseWrapper
from loaders import Course
import random, math

def get_option_count(wrapper, max_value, value):
    if isinstance(wrapper, Course.Course):
        if value > max_value:
            return max_value
        return 1*value
    else:
        if len(wrapper.AND) > 0:
            for x in wrapper.AND:
                if value > max_value:
                    return max_value
                value = value * wrapper.number_to_pick * get_option_count(x, max_value, value)
        else:
            for x in wrapper.OR:
                if value > max_value:
                    return max_value
                value = value * wrapper.number_to_pick * get_option_count(x, max_value, value)
    if value > max_value:
        return max_value
    return value

# beautiful
def pick_from_wrapper(wrapper, recur_pool):
    if isinstance(wrapper,Course.Course):
        if wrapper not in recur_pool:
            return recur_pool.append(wrapper) # append course
        else:
            return recur_pool
    elif len(wrapper.OR) > 0:
        # TODO: optimize here so user doesn't take weird prereq?
        picks = random.sample(range(len(wrapper.OR)), wrapper.number_to_pick)
        for i in picks:
            pick_from_wrapper(wrapper.OR[i], recur_pool)
    else:
        for x in wrapper.AND:
            # Because it is AND there is no option to pick a certain number
            pick_from_wrapper(x, recur_pool)
    return recur_pool

# returns list of courses coreqs, prereqs, and course (recursive)
# it was fun to debug...
def get_pre_co_list(course, course_list):
    if course in course_list:
        return
    if isinstance(course, Course.Course):
        pc = course.prereqs + course.coreq_list
        for x in pc:
            if x not in course_list and isinstance(x, Course.Course):
                course_list.append(x)
            if x not in course_list:
                get_pre_co_list(x, course_list)
        if course not in course_list:
            course_list.append(course)
    elif type(course) is list:
        for x in course:
            get_pre_co_list(x, course_list)
    elif isinstance(course, CourseWrapper.CourseWrapper):
        temp = pick_from_wrapper(course, [])
        for x in temp:
            if x not in course_list:
                get_pre_co_list(x, course_list)

def add_percents_priorites(course_options):
    # TODO actually implement getting this stuff from database -- for now there are just hard-coded values for testing
    # TODO (not here) add class specific info to FINAL courses in schedules
    # TODO (not here) add check for missing info in course, try to find it in database if able (e.g. if units is missing, etc.)
    # TODO account for if user isn't taken a quarter
    # NOTE: we can change percentages and priorities however we want to move results

    """ TESTING CODE """
    # completely for tesitng, actual implementation will NOT be like this
    # courses will randomly pick 1 from each
    quarters_percents = {'Fall' : random.sample(range(100), 30) + [0] * 8, 'Winter': random.sample(range(100), 30) + [0] * 8,
                         'Spring':random.sample(range(100), 30) + [0] * 8}
    # extra 0's to make more likely course time not known or course not offered in that quarter
    priorities = random.sample(range(30), 30) # randomly pick one per course for now -- later will be user based,
    # and next highest priority will be highest courses in tree, with priorities dropping as levels drop

    for x in course_options:
        for option in x:
            for course in option:
                course.user_priority = priorities[random.randint(0, 29)]
                course.percent_chance_offered['Fall'] = quarters_percents['Fall'][random.randint(0, 30)]
                course.percent_chance_offered['Winter'] = quarters_percents['Winter'][random.randint(0, 30)]
                course.percent_chance_offered['Spring'] = quarters_percents['Spring'][random.randint(0, 30)]

    """"""""""""
def recursively_append_to_remove(course, to_remove):
    """ function appends courses to 'to_remove' list which the user has taken.
    In other words, if the user has taken x, and y is a coreq or prereq to x, x,y and all coreqs/prereqs to their prereqs
    (and so on) will be added to the 'to_remove' list """
    if isinstance(course, CourseWrapper.CourseWrapper):
        if len(course.AND) > 0:
            for x in course.AND:
                recursively_append_to_remove(x, to_remove)
        else: # OR
            for x in course.OR:
                recursively_append_to_remove(x, to_remove)
        return
    coreqs_prereqs = course.prereqs + course.coreq_list
    for x in coreqs_prereqs:
        if x not in to_remove:
            recursively_append_to_remove(x, to_remove)
    if course not in to_remove:
        to_remove.append(course)

def remove_certian_course_options(pool, runtime_vars):
    # TODO: CHECK IF THIS ACTUALLY WORKS (I'm only partially joking)
    to_remove = []  # courses and entire options to remove
    blacklisted = {}  # do not pick options for final pool which have courses which have blacklisted one another --
    courses_with_special_ids = []  # course objects with ids which will need to be accounted for
    # blacklisted contains strings, not course objects
    flatten = lambda *n: (e for a in n
                          for e in (flatten(*a) if isinstance(a, (tuple, list)) else (a,)))
    all_course_names = [x.course_name for x in flatten(pool)]
    for options in pool:
        double_break = False  # to break out of 2nd loop as well when breaking out of 3rd
        for option in options:
            if double_break:
                double_break = False
                break
            course_names_in_option = [course.course_name for course in option]
            for course in option:
                if course.course_name in runtime_vars['user_has_taken']:
                    recursively_append_to_remove(course, to_remove)
                # NOTE: may need to add things here
                if course.variables:
                    if runtime_vars['upper_div_student'] and 'lower_div_only' in course.variables:
                        to_remove.append(option)
                        double_break = True
                        break
                    for var in course.variables:
                        # if placement score or test score gets user out of course, remove course and related items
                        if var in runtime_vars and ('ap_' in var or 'act_' in var or 'sat_' in var) and \
                                        int(runtime_vars[var]) >= int(
                                    course.variables[var]):  # TODO, make types compatible
                            recursively_append_to_remove(course, to_remove)
                        # check ids
                        if 'id_' in var:
                            if course not in courses_with_special_ids:
                                courses_with_special_ids.append(course)
                        # this shouldn't even happen
                        if 'do_not_take' in var:
                            to_remove.append(option)
                            double_break = True
                            break
                        if 'blacklist' in var:
                            for course_name in course_names_in_option:

                                if course_name in course.variables[var]:
                                    # print(course.variables[var][
                                    #          course.variables[var].index(course_name) + len(course_name)])
                                    if course.variables[var] \
                                            [course.variables[var].index(course_name) + len(course_name)] == ']':
                                        # extra conditional added for case where Econ1 and Econ 15A were being treated as the same course
                                        to_remove.append(option)
                                        double_break = True
                                        break
                            for course_name in all_course_names:
                                if course_name in course.variables[var]:
                                    blacklisted[course.course_name] = course_name
    if runtime_vars['debug']:
        print("*** TO REMOVE ***")
        print(to_remove)
        print("*************")
    new_options = []
    for x in pool:
        new_options.append([])
        for y in x:
            if y in to_remove:
                if len(x) > 1:  # can remove this option
                    # check to make sure at least 1 option in x is valid
                    found = False
                    for y1 in x:
                        if y1 not in to_remove:
                            found = True
                            break
                    if not found:
                        print('Error...Valid option not found')
                        exit()
                else:  # user must take this, but logically can't, there is some problem
                    print('Problem is here - random unique string right here')
                    exit()
            else:
                new_options[-1].append([])
                for z in y:
                    if z not in to_remove:
                        new_options[-1][-1].append(z)
                if len(new_options[-1][-1]) == 0:  # if user has met requirements for all courses in this option
                    del new_options[-1][-1]
        if len(new_options[-1]) == 0:
            del new_options[-1]
    return new_options,blacklisted, courses_with_special_ids

def make_feeder_pool(pool, runtime_vars, feeder_pool):
    new_options, blacklisted, courses_with_special_ids = remove_certian_course_options(pool, runtime_vars)
    # add likelyhood to be offered per quarter percentage and (user/our) priority
    add_percents_priorites(new_options)

    # CHANGE_VAR
    pool_length = 5 # 5 is a good number
    if runtime_vars['fast_track']:
        while len(feeder_pool) < 5:
            # if not possible break
            # pick shortest option from each x
            for x in new_options:
                pass
    else:
        while len(feeder_pool) < 5:
            # if not possible break
            pass
    # TODO check special ids
    # TODO check blacklisted
    # TODO pick x best options (based off of fast or not) and add to feeder pool

    # 0) DESIGN CHOICE: Readable code over efficiency...Remove prereqs/coreqs of taken courses and taken courses
        # (or tested out of courses), first remove all option choices with blacklisted stuff, bad id's
    # 1) do the picking in loop -- handle fast-track or user-preferred
    # 2) add to pool while pool < x # CHANGE_VAR
        # a) make sure no duplicates



def make_combos(runtime_vars):
    major_req = runtime_vars['course_info'][1]
    wrappers = []
    option_pool = []
    for x in major_req:
        if isinstance(x, CourseWrapper.CourseWrapper):
            wrappers.append(x)
        else:
            option_pool.append([[x]])

    for wrapper in wrappers:
        # NOTE: '# CHANGE_VAR' can be searched for in path for variables to tune runtime
        # CHANGE_VAR
        option_count = get_option_count(wrapper, 100, 1) # wrapper, max_options wanted, initial value
        option_pool2 = []
        # cap length of options at 1, half of total possible, or 100 - whichever is smallest
        while len(option_pool2) < math.ceil(option_count):
            temp = pick_from_wrapper(wrapper,[])
            if temp not in option_pool2:
                option_pool2.append(temp)
        option_pool.append(option_pool2)

    option_pool_final = [] # will be option pool including prereqs and coreqs
    for x in option_pool:
        temp_pool = []
        for y in x:
            temp_pool2 = []
            get_pre_co_list(y, temp_pool2)
            temp_pool.append(temp_pool2)
        option_pool_final.append(temp_pool)

    if runtime_vars['debug']:
        print('*** Options before filtering/making feeder_pool ***')
        for x in option_pool_final:
            print(x)
        print('*** End options ***')

    feeder_pool = []
    make_feeder_pool(option_pool_final, runtime_vars, feeder_pool)
    # TODO: add percents/priorities somehow
    # TODO return 2 items
    return feeder_pool # possibly return more





