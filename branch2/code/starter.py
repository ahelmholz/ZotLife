import sys

''' This will make sense later -- MUCH thought has gone into it and it is probably really confusing without implementation '''
class PrereqWrapper:
    def __init__(self, number_to_pick = 1):
        # check depth, can have multiple depths
        # check if type PrereqWrapper or Course when doing work (nesting)
        self.number_to_pick = number_to_pick # number needed to be taken out of group to meet requirement
        self.AND = []
        self.OR = []
        
    def __repr__(self):
        return '{}[AND: {}, OR: {}]'.format(self.number_to_pick, self.AND, self.OR)

# VERY powerful because it combines major info with specific, up to date class info for filtering

class Course:
    def __init__(self, course_name):
        self.course_name = course_name
        self.variables = {}
        self.comment = ''
        self.isRequiredByMajor = None # since dict will be initialized with all prereqs as well
        self.user_has_taken = None
        # preqs before course
        # list of Course and PrereqWrapper objects
        self.prereqs = []
        self.coreq_list = []
        self.classes = [] # loaded from database
        # what is this class a prereq for? - list of course objects
        # user can possibly take these courses after completing this course
        self.is_prereq_for = []
        # wrapper to say which courses have to be taken(AND/OR)
        # pull/store info from DB?
        # when is it offered?
        # TODO: keep list of CLASSES in course object, with the class class storing discussion sections, specific lab #'s, etc
        # could use old code

    def add_var(self, var, val):
        self.variables[var] = val

    def add_comment(self, comment):
        self.comment = comment

    def add_coreq(self, course_obj):
        if course_obj not in self.coreq_list:
            self.coreq_list.append(course_obj)

    def add_prereq(self, course_obj):
        if course_obj not in self.prereqs:
            self.prereqs.append(course_obj)

    def __str__(self):
        return 'Course name: {}\n\tvars: {}\n\tcomment: {}\n\tprereq_list: {}\n\tpreq_for_list: {}\n\t' \
               'coreq_list: {}'.format(
            self.course_name, self.variables, self.comment, self.prereqs, self.is_prereq_for, self.coreq_list)

    def __repr__(self):
        return self.course_name

    def add_is_prereq_for(self, course):
        self.is_prereq_for.append(course)

def get_major_file(institution, major, type, catalog_year, specialization=None):
    # basic checks of input to function -- won't catch everything (should be done elsewhere)
    # NOTE: revise tests?
    if not institution.isupper():
        print('Error 1 in get_major_file')
        exit()
    # NOTE: type will have to change later to include grad degrees/minors?
    if len(type) != 2 or (type != 'BS' and type != 'BA'):
        print('Error 2 in get_major_file')
        exit()
    if len(catalog_year) != 5 or catalog_year[2] != '-':
        print('Error 3 in get_major_file')

    path = '../universities/' + institution + '/majors/' + major + '.' + type + '.' + catalog_year
    if specialization is not None:
        path += '/' + specialization   # NOTE: may move location
    print(path)
    try:
        return open(path, "r")
    except:
        print('We do not support this yet')
        exit()

# line numbers provided when able -- if not, -1
def print_error(line_num):
    print('An error occurred while parsing major file at line {}. Exiting...'.format(line_num))
    exit()

def check_basic_syntax_and_remove_comments(major_file):
    ret_string = ''
    special_comment = ''
    open_square_count = 0
    open_par_count = 0
    line_number = 0
    for line in major_file:
        line_number += 1
        ignore_rest_of_line = False
        line_course_count = 0
        line_operator_count = 0
        for i in range(len(line)):
            if not ignore_rest_of_line:
                if line[i] == '#':
                    ignore_rest_of_line = True
                else:
                    if "'''" in line:
                        special_comment += line
                        break
                    elif line[i] == '[':
                        open_square_count += 1
                        if i > 0:
                            if line[i - 1] != ' ' and line[i - 1] != '(' and line[i - 1] != '*' and line[i - 1] != ',':
                                    print("Square bracket can only have (, ',', * or a space outside of it")
                                    print_error(line_number)
                    elif line[i] == ']':
                        if i + 1 < len(line):
                            if line[i + 1] != ' ' and line[i + 1] != ')' and line[i +1] != '\n' and line[i + 1] != ',':
                                    print("Square bracket can only have ), ',', \\n or a space outside of it")
                                    print_error(line_number)
                        open_square_count -= 1
                        line_course_count += 1
                        if open_square_count < 0:
                            print_error(line_number)
                    elif line[i] == '(':
                        open_par_count += 1
                    elif line[i] == ')':
                        open_par_count -= 1
                        if open_par_count < 0:
                            print_error(line_number)
                    elif open_square_count == 0 and (line[i] == 'A' or line[i] == 'O'):
                        line_operator_count += 1
                        if i > 0:
                            if line[i - 1] != ' ' and line[i - 1] != '\n' and line[i - 1] != '\\':
                                    print("A and O must have a space on each side")
                                    print_error(line_number)
                        if i + 1 < len(line):
                            if line[i + 1] != ' ' and line[i + 1] != '\n' and line[i + 1] != '\\':
                                    print("A and O must have a space on each side")
                                    print_error(line_number)
                    if line[i] == '\n' and line_operator_count > line_course_count:
                        print('More operators than courses')
                        print_error(-1)
                    # add char to ret_object
                    ret_string += line[i]
            else:
                if line[i] == '\n':
                    ret_string += line[i]
                    ignore_rest_of_line = False
                    if line_operator_count > line_course_count:
                        print('More operators than courses')
                        print_error(-1)
    if open_square_count > 0 or open_par_count > 0:
        print_error(-1)
    # remove quotes from special comment
    special_comment = special_comment.replace("'''", "").strip()
    return (special_comment, ret_string.strip())

# stores info from both .maj file and class database
def load_major_courses_into_data_structure(major_file):

    # recursion makes life easier
    # I don't want to explain how this works
    # PRECONDITION: expression is surrounded by parenthesis
    # when '(' is reached, prereq wrapper ref is pushed on stack
    # when ')' is reached, prereq wrapper ref is popped from stack

    def recur_parse(index, line, working_course, course_dict):

        if index == 0:
            recur_parse.wrapper_stack = []
            recur_parse.isFirst = True
            recur_parse.lastOperator = 'A'  # defaults to AND
            recur_parse.char_in_course = False  # to say whether recursive function is inside of a course name [] or out
            recur_parse.course_name = ''
            recur_parse.temp_course = None
            recur_parse.firstCourseEntered = False
        # base case
        if index == len(line) - 2:
            return
        if line[index] == '(':
            if index > 0 and line[index - 1].isdigit():
                recur_parse.wrapper_stack.append(PrereqWrapper(int(line[index - 1])))
            else:
                recur_parse.wrapper_stack.append(PrereqWrapper())
            # at this point, top of stack is new wrapper
            if recur_parse.isFirst:
                working_course.add_prereq(recur_parse.wrapper_stack[-1])
                recur_parse.isFirst = False
            else:
                if recur_parse.lastOperator == 'A':
                    recur_parse.wrapper_stack[-2].AND.append(recur_parse.wrapper_stack[-1])
                else:
                    recur_parse.wrapper_stack[-2].OR.append(recur_parse.wrapper_stack[-1])
        # pop off
        elif line[index] == ')':
            recur_parse.wrapper_stack = recur_parse.wrapper_stack[0:-1]
        elif not recur_parse.char_in_course and line[index] == 'A':
            recur_parse.lastOperator = 'A'
        elif not recur_parse.char_in_course and line[index] == 'O':
            recur_parse.lastOperator = 'O'
        elif line[index] == '[':
            recur_parse.char_in_course = True
        elif line[index] == ']':
            recur_parse.char_in_course = False
            if recur_parse.course_name not in course_dict:
                course_dict[recur_parse.course_name] = Course(recur_parse.course_name)
                course_dict[recur_parse.course_name].add_is_prereq_for(working_course)
                working_course.add_prereq(course_dict[recur_parse.course_name])
                if not recur_parse.firstCourseEntered:
                    recur_parse.temp_course = recur_parse.course_name
                    recur_parse.firstCourseEntered = True
                elif recur_parse.lastOperator == 'A':
                    recur_parse.wrapper_stack[-1].AND.append(course_dict[recur_parse.course_name])
                    if recur_parse.temp_course is not None:
                        course_dict[recur_parse.temp_course] = Course(recur_parse.temp_course)
                        course_dict[recur_parse.temp_course].add_is_prereq_for(working_course)
                        working_course.add_prereq(course_dict[recur_parse.temp_course])
                        recur_parse.wrapper_stack[-1].AND.append(course_dict[recur_parse.temp_course])
                        recur_parse.temp_course = None
                else:
                    recur_parse.wrapper_stack[-1].OR.append(course_dict[recur_parse.course_name])
                    if recur_parse.temp_course is not None:
                        course_dict[recur_parse.temp_course] = Course(recur_parse.temp_course)
                        course_dict[recur_parse.temp_course].add_is_prereq_for(working_course)
                        working_course.add_prereq(course_dict[recur_parse.temp_course])
                        recur_parse.wrapper_stack[-1].OR.append(course_dict[recur_parse.temp_course])
                        recur_parse.temp_course = None
            recur_parse.course_name = ''
        elif recur_parse.char_in_course:
            recur_parse.course_name += line[index]
        recur_parse(index + 1, line, working_course, course_dict)

    # put courses in dictionary for loading all info easily and efficiently
    # will make objects from below
    course_dict = {}

    # will be a tuple, the first string being the comment to the user about the major, the second being the remaining text
    major_strings = check_basic_syntax_and_remove_comments(major_file)
    #print(major_strings[1])
    # at this point, ''' ''' and # are stripped, somewhat valid parenthesis have been checked for

    # split lines into two -- first half is major outline -- second half is course requirements
    expression = ''
    first_half = major_strings[1][:major_strings[1].index('*') - 1] # major requirements
    second_half = major_strings[1][major_strings[1].index('*'):] # course requirements

    # process courses first
    for course in second_half.split('*')[1:]:
        # first course is course to open
        name = course[course.index('[') + 1: course.index(']')]
        working_course = None
        if name in course_dict:
            working_course = course_dict[name]
        else:
            working_course = Course(name)
        local_expression = ''
        # skipping first line which was course to open
        for line in course.splitlines()[1:]:
            if '\\' in line.strip()[-1:]:
                local_expression_terminated = False
                local_expression += line[0:-1]
            else:
                local_expression_terminated = True
                local_expression += ' ' + line # in case of line being continued =
                local_expression = local_expression.strip()
            if local_expression_terminated:
                # process expression here
                # is var?
                if '=' in line:
                    # NOTE: get important variables here, if not they are put into generic course variabes
                    temp = [i.strip() for i in line.split('=')]
                    # NOTE: some redundancy with coreq stuff, 'C' and 'coreq =' are parsed to be safe
                    if 'coreq' in temp[0]:
                        if ',' not in temp[1]:
                            name = temp[1][1:-1]
                            if name not in course_dict:
                                course_dict[name] = Course(name)
                            working_course.add_coreq(course_dict[name])
                            course_dict[name].add_coreq(working_course)
                        else:
                            names = [i.strip()[1:-1] for i in temp[1].split(',')]
                            for name in names:
                                if name not in course_dict:
                                    course_dict[name] = Course(name)
                                working_course.add_coreq(course_dict[name])
                                course_dict[name].add_coreq(working_course)
                    # elif here for grabbing additional important variables
                    else:
                        working_course.add_var(temp[0], temp[1])
                # course comment
                elif '$' in line:
                    line = line[line.index("'") + 1:]
                    working_course.add_comment(line[:line.index("'")].strip())
                # prereqs
                elif '[' in line:
                    # no prereq wrapper needed
                    if line.count('[') == 1:
                        name = line[line.index('[') + 1: line.index(']')]
                        if name not in course_dict:
                            course_dict[name] = Course(name)
                        course_dict[name].add_is_prereq_for(working_course)
                        working_course.add_prereq(course_dict[name])
                    # wrapper needed
                    else:
                        if '(' not in line and ')' not in line:
                            # if there is no ( in the line, line must only have one type of operator
                            if ' A ' in line:
                                # create wrapper
                                prw = PrereqWrapper()
                                temp = line.split(' A ')
                                temp_2 = [i.strip()[1:-1] for i in temp if '[' in i and ']' in i]
                                for name in temp_2:
                                    if name not in course_dict:
                                        course_dict[name] = Course(name)
                                        if working_course not in course_dict[name].is_prereq_for:
                                            course_dict[name].add_is_prereq_for(working_course)
                                    prw.AND.append(course_dict[name])
                                working_course.add_prereq(prw)
                            elif ' O ' in line:
                                # create wrapper
                                prw = PrereqWrapper()
                                temp = line.split(' O ')
                                temp_2 = [i.strip()[1:-1] for i in temp if '[' in i and ']' in i]
                                for name in temp_2:
                                    if name not in course_dict:
                                        course_dict[name] = Course(name)
                                        if working_course not in course_dict[name].is_prereq_for:
                                            course_dict[name].add_is_prereq_for(working_course)
                                    prw.OR.append(course_dict[name])
                                working_course.add_prereq(prw)
                            else:
                                print("Something went wrong 98787 - random number to search in code")
                                print_error(-1)
                        # could have depth
                        else:
                            recur_parse(0,line.strip(), working_course, course_dict)

                course_dict[working_course.course_name] = working_course
                local_expression = ''
    ###
    for key, val in course_dict.items():
        print(val)
        print()
    ###
    """ ******************* WORKING HERE ******************* """
    # TODO: TEST, continue coding below
    # take stuff from above
    # add to course if it is required
    # add to coreqs?
    # process major requirements
    expression_terminated = None
    for line in first_half.splitlines():
        if '\\' in line.strip()[-1:]:
            expression_terminated = False
            expression += line[0:-1]
        else:
            expression_terminated = True
            expression += line
        if expression_terminated:
            # process expression here
            #print(expression)
            # WORKING HERE 
            expression = ''




    # define what needs to be returned
    # return the courses here
    """"""""""""""""""""""""""

    # data structure will have what's required to get degree, and also courses in dict
    return True

""" JUST FOR TESTING -- Make into functions/API later"""
#institution = input("Institution: ")
#major = input("Major: ")
#BS_BA_Other = input("BS, BA or other?")
#year_declared_under = input("What year are you declaring under?")
#specialization = input("Do you have a specialization? (y/n)")
#if 'n' in specialization.lower():
#    specialization = None
#else:
#    specialization = input("What is your specialization?")

# TODO: get classes already taken
# TODO: load school info file


# build file path off of info
# try to get file, if not there 'Sorry, we don't support this yet'
#major_file = get_major_file(institution, major, BS_BA_Other, year_declared_under, specialization)

""" TO SAVE EFFORT DURING TESTING """
major_file = open("../universities/UCSC/CMPS.BS.16-17", "r")
""""""
# will load info from the major file, make objects with info from both file and course DB
courses = None
try:
    courses = load_major_courses_into_data_structure(major_file)
except Exception as e:
    print(str(e))
    print('We do not support this major at this University yet.')