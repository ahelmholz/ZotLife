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

def add_percents_priorites():
    pass

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

def make_feeder_pool(pool, runtime_vars, feeder_pool):
    # TODO: CHECK IF THIS WORKS
    to_remove = [] # courses and entire options to remove
    blacklisted = {} # do not pick options for final pool which have courses which have blacklisted one another --
    # blacklisted contains strings, not course objects
    flatten = lambda *n: (e for a in n
                          for e in (flatten(*a) if isinstance(a, (tuple, list)) else (a,)))
    all_course_names = [x.course_name for x in flatten(pool)]
    for options in pool:
        double_break = False # to break out of 2nd loop as well when breaking out of 3rd
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
                    id_count = {}
                    for var in course.variables:
                        # if placement score or test score gets user out of course, remove course and related items
                        if var in runtime_vars and ('ap_' in var or 'act_' in var or 'sat_' in var) and \
                            int(runtime_vars[var]) >= int(course.variables[var]): # TODO, make types compatible
                            recursively_append_to_remove(course, to_remove)
                        # check ids
                        if 'id_' in var:
                            if var not in id_count:
                                id_count[var] = 0
                            id_count[var] += 1
                            if int(course.variables[var]) < id_count[var]:
                                to_remove.append(option)
                                double_break = True
                                break
                        # this shouldn't even happen
                        if 'do_not_take' in var:
                            to_remove.append(option)
                            double_break = True
                            break
                        if 'blacklist' in var:
                            for course_name in course_names_in_option:

                                if course_name in course.variables[var]:
                                    #print(course.variables[var][
                                    #          course.variables[var].index(course_name) + len(course_name)])
                                    if course.variables[var]\
                                    [course.variables[var].index(course_name) + len(course_name)] == ']':
                                    # extra conditional added for case where Econ1 and Econ 15A were being treated as the same course
                                        to_remove.append(option)
                                        double_break = True
                                        break
                            for course_name in all_course_names:
                                if course_name in course.variables[var]:
                                    blacklisted[course.course_name] = course_name
    # TODO from pool remove to_remove course items
    # TODO if removal of list makes list empty, PROBLEM
    # TODO check blacklisted
    # TODO pick x best options (based off of fast or not) and add to feeder pool
    if runtime_vars['debug']:
        print("*** TO REMOVE ***")
        print(to_remove)
        print("*************")
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
    return feeder_pool # possibly return more





