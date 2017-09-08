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

def make_feeder_pool(pool, runtime_vars, feeder_pool):
    feeder_pool.append('Hello, world!')
    # TODO
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





