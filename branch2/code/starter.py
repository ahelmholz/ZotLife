class CourseWrapper:
    def __init__(self, number_to_pick = 1):
        # check depth, can have multiple depths
        # check if type CourseWrapper or Course when doing work (nesting)
        self.number_to_pick = number_to_pick # number needed to be taken out of group to meet requirement
        self.AND = []
        self.OR = []
        
    def __repr__(self):
        return '{}{}AND: {}, OR: {}{}'.format(self.number_to_pick, '{', self.AND, self.OR, '}')

class Course:
    def __init__(self, course_name):
        self.course_name = course_name
        self.variables = {}
        self.comment = ''
        # isRequiredOption means course is in major outline (may be optional -- but still in major outline)
        self.isRequiredOption = False # since course_dict will be initialized with all prereqs as well
        self.user_has_taken = None
        # preqs before course
        # list of Course and CourseWrapper objects
        self.prereqs = []
        self.coreq_list = []
        self.classes = [] # loaded from database
        # user can possibly take these courses after completing this course
        self.is_prereq_for = []
        # pull/store info from DB?
        # when is it offered?
        self.course_offered_in = [] # FALL, WINTER, SPRING, SUMMER -- find out/add options from DB?
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

    def returnInfo(self):
        return 'Course name: {}\n\tvars: {}\n\tcomment: {}\n\tprereq_list: {}\n\tpreq_for_list: {}\n\t' \
               'coreq_list: {}\n\tisRequiredOption: {}'.format(
            self.course_name, self.variables, self.comment, self.prereqs, self.is_prereq_for, self.coreq_list,
            self.isRequiredOption)

    def __str__(self):
        return self.course_name

    def __repr__(self):
        return self.course_name

    def add_is_prereq_for(self, course):
        if course not in self.is_prereq_for:
            self.is_prereq_for.append(course)

def get_major_and_school_files(institution, major, type, catalog_year, specialization=None):
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
    #print(path)
    # TODO: may need to change this if different schools within University are supported
    school_path = '../universities/' + institution + '/' + institution + '.info'
    try:
        return open(school_path, "r"), open(path, "r")
    except:
        print('We do not support this yet')
        exit()


# line numbers provided when able -- if not, -1
def print_error(line_num):
    print('An error occurred while parsing major file at line {}. Exiting...'.format(line_num))
    exit()

def check_basic_syntax_and_remove_comments(major_file, debug_enabled=False):
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
                    elif debug_enabled:
                        if line[i] == '[':
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
                    if debug_enabled and (line_operator_count > line_course_count):
                        print('More operators than courses')
                        print_error(-1)
    if debug_enabled and (open_square_count > 0 or open_par_count > 0):
        print_error(-1)
    # remove quotes from special comment
    special_comment = special_comment.replace("'''", "").strip()
    return (special_comment, ret_string.strip())

def load_school_vars(school_file):
    school_vars = {}
    # remove comments
    for line in school_file:
        if '#' in line:
            line = line[0:line.index('#')]
        if '=' in line:
            temp = line.split('=')
            school_vars[temp[0].strip()] = temp[1].strip()
    return school_vars

# stores info from both .maj file and class database
def load_major_courses_into_data_structure(major_file, debug_enabled=False):

    # recursion makes life easier
    # I don't want to explain how this works
    # PRECONDITION: expression is surrounded by parenthesis
    # when '(' is reached, prereq wrapper ref is pushed on stack
    # when ')' is reached, prereq wrapper ref is popped from stack
    # MUST have index as 0 passed in at first to reset function
    
    # for parsing 2nd half of file (course prereqs)
    def recur_parse_prereqs(index, line, working_course, course_dict):
        if index == 0:
            recur_parse_prereqs.wrapper_stack = []
            recur_parse_prereqs.isFirst = True
            recur_parse_prereqs.lastOperator = 'A'  # defaults to AND
            recur_parse_prereqs.char_in_course = False  # to say whether recursive function is inside of a course name [] or out
            recur_parse_prereqs.course_name = ''
            recur_parse_prereqs.temp_course = None
            recur_parse_prereqs.firstCourseEntered = False
            recur_parse_prereqs.last_prereq_operator = 'A'
            recur_parse_prereqs.isFirstWrapper = True
        # base case
        if index == len(line) - 1 or len(line) < 2:
            return
        if line[index] == '(':
            recur_parse_prereqs.last_prereq_operator = recur_parse_prereqs.lastOperator
            if index > 0 and line[index - 1].isdigit():
                recur_parse_prereqs.wrapper_stack.append(CourseWrapper(int(line[index - 1])))
            else:
                recur_parse_prereqs.wrapper_stack.append(CourseWrapper())
            # at this point, top of stack is new wrapper
            if recur_parse_prereqs.isFirst:
                working_course.add_prereq(recur_parse_prereqs.wrapper_stack[-1])
                recur_parse_prereqs.isFirst = False
            else:
                if recur_parse_prereqs.isFirstWrapper:
                    recur_parse_prereqs.isFirstWrapper = False
                    A_found = False
                    count = 0
                    real_count = 0
                    for i in range(0, len(line)):
                        if line[i] == '(':
                            count += 1
                            real_count += 1
                        elif line[i] == ')':
                            count -= 1
                        if count == 1 and real_count > count:
                            if ' A ' in line[i - 2:i+5]:
                                A_found = True # else OR
                                break
                            elif ' O ' in line[i - 2:i+5]:
                                break
                            else:
                                print("ERROR in parsing 3333")
                                print(line[i - 2:i+5])
                    if A_found:
                        recur_parse_prereqs.wrapper_stack[-2].AND.append(recur_parse_prereqs.wrapper_stack[-1])
                    else: # OR
                        recur_parse_prereqs.wrapper_stack[-2].OR.append(recur_parse_prereqs.wrapper_stack[-1])

                else:
                    if recur_parse_prereqs.last_prereq_operator == 'A':
                        recur_parse_prereqs.wrapper_stack[-2].AND.append(recur_parse_prereqs.wrapper_stack[-1])
                    else:
                        recur_parse_prereqs.wrapper_stack[-2].OR.append(recur_parse_prereqs.wrapper_stack[-1])
            recur_parse_prereqs.firstCourseEntered = False
        # pop off
        elif line[index] == ')':
            recur_parse_prereqs.wrapper_stack = recur_parse_prereqs.wrapper_stack[0:-1]
            if len(recur_parse_prereqs.wrapper_stack) == 0:
                line = ''
                recur_parse_prereqs(index + 1, line, working_course, course_dict)
        elif not recur_parse_prereqs.char_in_course and line[index] == 'A':
            recur_parse_prereqs.lastOperator = 'A'
        elif not recur_parse_prereqs.char_in_course and line[index] == 'O':
            recur_parse_prereqs.lastOperator = 'O'
        elif line[index] == '[':
            recur_parse_prereqs.char_in_course = True
        elif line[index] == ']':
            recur_parse_prereqs.char_in_course = False
            if recur_parse_prereqs.course_name not in course_dict:
                course_dict[recur_parse_prereqs.course_name] = Course(recur_parse_prereqs.course_name)
                course_dict[recur_parse_prereqs.course_name].add_is_prereq_for(working_course)
            if not recur_parse_prereqs.firstCourseEntered:
                if recur_parse_prereqs.temp_course is not None:
                    if recur_parse_prereqs.lastOperator == 'A':
                        if recur_parse_prereqs.temp_course not in course_dict:
                            course_dict[recur_parse_prereqs.temp_course] = Course(recur_parse_prereqs.temp_course)
                        course_dict[recur_parse_prereqs.temp_course].add_is_prereq_for(working_course)
                        recur_parse_prereqs.wrapper_stack[-2].AND.append(course_dict[recur_parse_prereqs.temp_course])
                    else:
                        if recur_parse_prereqs.temp_course not in course_dict:
                            course_dict[recur_parse_prereqs.temp_course] = Course(recur_parse_prereqs.temp_course)
                        course_dict[recur_parse_prereqs.temp_course].add_is_prereq_for(working_course)
                        recur_parse_prereqs.wrapper_stack[-2].OR.append(course_dict[recur_parse_prereqs.temp_course])
                recur_parse_prereqs.temp_course = recur_parse_prereqs.course_name
                recur_parse_prereqs.firstCourseEntered = True
            elif recur_parse_prereqs.lastOperator == 'A':
                recur_parse_prereqs.wrapper_stack[-1].AND.append(course_dict[recur_parse_prereqs.course_name])
                if recur_parse_prereqs.temp_course is not None:
                    if recur_parse_prereqs.temp_course not in course_dict:
                        course_dict[recur_parse_prereqs.temp_course] = Course(recur_parse_prereqs.temp_course)
                    course_dict[recur_parse_prereqs.temp_course].add_is_prereq_for(working_course)
                    recur_parse_prereqs.wrapper_stack[-1].AND.append(course_dict[recur_parse_prereqs.temp_course])
                    recur_parse_prereqs.temp_course = None
            else:
                recur_parse_prereqs.wrapper_stack[-1].OR.append(course_dict[recur_parse_prereqs.course_name])
                if recur_parse_prereqs.temp_course is not None:
                    if recur_parse_prereqs.temp_course not in course_dict:
                        course_dict[recur_parse_prereqs.temp_course] = Course(recur_parse_prereqs.temp_course)
                    course_dict[recur_parse_prereqs.temp_course].add_is_prereq_for(working_course)
                    recur_parse_prereqs.wrapper_stack[-1].OR.append(course_dict[recur_parse_prereqs.temp_course])
                    recur_parse_prereqs.temp_course = None
            recur_parse_prereqs.course_name = ''
        elif recur_parse_prereqs.char_in_course:
            recur_parse_prereqs.course_name += line[index]
        recur_parse_prereqs(index + 1, line, working_course, course_dict)

    # for parsing major requirements (first half of file)
    # preconditions same as recur_parse_prereqs
    def recur_parse_major_reqs(index, line, major_list, course_dict):
        if index == 0:
            recur_parse_major_reqs.wrapper_stack = []
            recur_parse_major_reqs.isFirst = True
            recur_parse_major_reqs.lastOperator = 'A'  # defaults to AND
            recur_parse_major_reqs.char_in_course = False  # to say whether recursive function is inside of a course name [] or out
            recur_parse_major_reqs.course_name = ''
            recur_parse_major_reqs.temp_course = None
            recur_parse_major_reqs.firstCourseEntered = False
            recur_parse_major_reqs.last_prereq_operator = 'A'
            recur_parse_major_reqs.isFirstWrapper = True
        # base case
        if index == len(line) - 1 or len(line) < 2:
            return
        if line[index] == '(':
            recur_parse_major_reqs.last_prereq_operator = recur_parse_major_reqs.lastOperator
            if index > 0 and line[index - 1].isdigit():
                recur_parse_major_reqs.wrapper_stack.append(CourseWrapper(int(line[index - 1])))
            else:
                recur_parse_major_reqs.wrapper_stack.append(CourseWrapper())
            # at this point, top of stack is new wrapper
            if recur_parse_major_reqs.isFirst:
                major_list.append(recur_parse_major_reqs.wrapper_stack[-1])
                recur_parse_major_reqs.isFirst = False
            else:
                if recur_parse_major_reqs.isFirstWrapper:
                    recur_parse_major_reqs.isFirstWrapper = False
                    A_found = False
                    count = 0
                    real_count = 0
                    for i in range(0, len(line)):
                        if line[i] == '(':
                            count += 1
                            real_count += 1
                        elif line[i] == ')':
                            count -= 1
                        if count == 1 and real_count > count:
                            if ' A ' in line[i - 2:i + 5]:
                                A_found = True  # else OR
                                break
                            elif ' O ' in line[i - 2:i + 5]:
                                break
                            else:
                                print("ERROR in parsing 338833")
                                print(line[i - 2:i + 5])
                    if A_found:
                        recur_parse_major_reqs.wrapper_stack[-2].AND.append(recur_parse_major_reqs.wrapper_stack[-1])
                    else:  # OR
                        recur_parse_major_reqs.wrapper_stack[-2].OR.append(recur_parse_major_reqs.wrapper_stack[-1])

                else:
                    if recur_parse_major_reqs.last_prereq_operator == 'A':
                        recur_parse_major_reqs.wrapper_stack[-2].AND.append(recur_parse_major_reqs.wrapper_stack[-1])
                    else:
                        recur_parse_major_reqs.wrapper_stack[-2].OR.append(recur_parse_major_reqs.wrapper_stack[-1])
            recur_parse_major_reqs.firstCourseEntered = False
        # pop off
        elif line[index] == ')':
            recur_parse_major_reqs.wrapper_stack = recur_parse_major_reqs.wrapper_stack[0:-1]
            if len(recur_parse_major_reqs.wrapper_stack) == 0:
                line = ''
                recur_parse_major_reqs(index + 1, line, major_list, course_dict)
        elif not recur_parse_major_reqs.char_in_course and line[index] == 'A':
            recur_parse_major_reqs.lastOperator = 'A'
        elif not recur_parse_major_reqs.char_in_course and line[index] == 'O':
            recur_parse_major_reqs.lastOperator = 'O'
        elif line[index] == '[':
            recur_parse_major_reqs.char_in_course = True
        elif line[index] == ']':
            recur_parse_major_reqs.char_in_course = False
            if recur_parse_major_reqs.course_name not in course_dict:
                print('{} does not have a course entry. Exiting.'.format(recur_parse_major_reqs.course_name))
                exit()
            course_dict[recur_parse_major_reqs.course_name].isRequiredOption = True
            if not recur_parse_major_reqs.firstCourseEntered:
                if recur_parse_major_reqs.temp_course is not None:
                    if recur_parse_major_reqs.lastOperator == 'A':
                        recur_parse_major_reqs.wrapper_stack[-2].AND.append(
                            course_dict[recur_parse_major_reqs.temp_course])
                    else:
                        recur_parse_major_reqs.wrapper_stack[-2].OR.append(
                            course_dict[recur_parse_major_reqs.temp_course])
                recur_parse_major_reqs.temp_course = recur_parse_major_reqs.course_name
                recur_parse_major_reqs.firstCourseEntered = True
            elif recur_parse_major_reqs.lastOperator == 'A':
                recur_parse_major_reqs.wrapper_stack[-1].AND.append(course_dict[recur_parse_major_reqs.course_name])
                if recur_parse_major_reqs.temp_course is not None:
                    recur_parse_major_reqs.wrapper_stack[-1].AND.append(course_dict[recur_parse_major_reqs.temp_course])
                    recur_parse_major_reqs.temp_course = None
            else:
                recur_parse_major_reqs.wrapper_stack[-1].OR.append(course_dict[recur_parse_major_reqs.course_name])
                if recur_parse_major_reqs.temp_course is not None:
                    recur_parse_major_reqs.wrapper_stack[-1].OR.append(course_dict[recur_parse_major_reqs.temp_course])
                    recur_parse_major_reqs.temp_course = None
            recur_parse_major_reqs.course_name = ''
        elif recur_parse_major_reqs.char_in_course:
            recur_parse_major_reqs.course_name += line[index]
        recur_parse_major_reqs(index + 1, line, major_list, course_dict)

    # put courses in dictionary for loading all info easily and efficiently
    course_dict = {}

    # will be a tuple, the first string being the comment to the user about the major, the second being the remaining text
    major_strings = check_basic_syntax_and_remove_comments(major_file, debug_enabled)
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
                #local_expression += ' ' + local_expression # in case of local_expression being continued =
                local_expression = local_expression.strip() + ' ' + line.strip()
                local_expression = local_expression.strip()
            if local_expression_terminated:
                # process expression here
                # is var?
                if '=' in local_expression:
                    # NOTE: get important variables here, if not they are put into generic course variables
                    temp = [i.strip() for i in local_expression.split('=')]
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
                elif '$' in local_expression:
                    local_expression = local_expression[local_expression.index("'") + 1:]
                    working_course.add_comment(local_expression[:local_expression.index("'")].strip())
                # prereqs
                elif '[' in local_expression:
                    # no prereq wrapper needed
                    if local_expression.count('[') == 1:
                        name = local_expression[local_expression.index('[') + 1: local_expression.index(']')]
                        if name not in course_dict:
                            course_dict[name] = Course(name)
                        course_dict[name].add_is_prereq_for(working_course)
                        working_course.add_prereq(course_dict[name])
                    # wrapper needed
                    else:
                        if '(' not in local_expression and ')' not in local_expression:
                            # if there is no ( in the local_expression, local_expression must only have one type of operator
                            if ' A ' in local_expression:
                                # create wrapper
                                prw = CourseWrapper()
                                temp = local_expression.split(' A ')
                                temp_2 = [i.strip()[1:-1] for i in temp if '[' in i and ']' in i]
                                for name in temp_2:
                                    if name not in course_dict:
                                        course_dict[name] = Course(name)
                                        if working_course not in course_dict[name].is_prereq_for:
                                            course_dict[name].add_is_prereq_for(working_course)
                                    prw.AND.append(course_dict[name])
                                working_course.add_prereq(prw)
                            elif ' O ' in local_expression:
                                # create wrapper
                                prw = CourseWrapper()
                                temp = local_expression.split(' O ')
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
                            recur_parse_prereqs(0,local_expression.strip(), working_course, course_dict)

                course_dict[working_course.course_name] = working_course
                local_expression = ''
    expression_terminated = None
    major_list = []
    for line in first_half.splitlines():
        if '\\' in line.strip()[-1:]:
            expression_terminated = False
            expression += line[0:-1]
        else:
            expression_terminated = True
            expression += line
        if expression_terminated and len(expression) > 0:
            # if elective
            if len(expression) < 5 and 'E' in expression:
                print('\n(((( Electives need to be handled ))))\n')
                # TODO: handle electives -- keep needed vars on this line, e.g. from_upper_div = 2, from_lower_div = 2
            # process expression here
            #print(expression)
            elif '(' in expression:
                recur_parse_major_reqs(0, expression, major_list, course_dict)
                #print(major_list)
            elif expression.count('[') > 1:
                # if there is no ( in the expression, expression must only have one type of operator
                if ' A ' in expression:
                    # create wrapper
                    prw = CourseWrapper()
                    temp = expression.split(' A ')
                    temp_2 = [i.strip()[1:-1] for i in temp if '[' in i and ']' in i]
                    for name in temp_2:
                        if name not in course_dict:
                            print('No entry for {} in courses'.format(name))
                            exit()
                        course_dict[name].isRequiredOption = True
                        prw.AND.append(course_dict[name])
                    major_list.append(prw)
                elif ' O ' in expression:
                    # create wrapper
                    prw = CourseWrapper()
                    temp = expression.split(' O ')
                    temp_2 = [i.strip()[1:-1] for i in temp if '[' in i and ']' in i]
                    for name in temp_2:
                        if name not in course_dict:
                            print('No entry for {} in courses'.format(name))
                            exit()
                        course_dict[name].isRequiredOption = True
                        prw.OR.append(course_dict[name])
                    major_list.append(prw)
                else:
                    print("Something went wrong 87787 - random number to search in code")
                    print_error(-1)
            # single course
            else:
                name = expression[expression.index('[') + 1: expression.index(']')]
                if name not in course_dict:
                    print('{} does not have a course entry'.format(name))
                    exit()
                major_list.append(course_dict[name])
                course_dict[name].isRequiredOption = True
            expression = ''

    # function returns tuple, [0] is major comment, [1] is list of major requirements, [2] is dictionary of course info
    return (major_strings[0], major_list, course_dict)

# TODO: move TODOs
# TODO: get classes already taken
# TODO: load school info file -- get max units allowed per time - default if not
# TODO: check all variables when building schedule
# TODO: make into API-ish format
# TODO: write algorithms to step through and build schedule
# TODO: build in check for if class has a typo -- cross check with course DB
# -- final safety is already saying we don't support it in case something goes wrong ;)

def printDebugInfo(info_tuple, school_vars, major_file, school_file):
    print("Number of courses in course_dict: {}".format(len(info_tuple[2])))
    print('Files:')
    print('{}\n{}\n'.format(major_file.name, school_file.name))
    print("******  MAJOR STRING *******")
    print(info_tuple[0])
    print("\n*** MAJOR REQUIREMENTS ***")
    for x in info_tuple[1]:
        print('\t' + str(x))
    print("\n******** COURSES ********")
    for key, value in info_tuple[2].items():
        print(value.returnInfo())
        print()
    print("\n******** SCHOOL VARS ********")
    print(school_vars)

""" TO SAVE EFFORT DURING TESTING """
#TODO: remove this
major_file = open("../universities/UCI/majors/SOCIOL.BA.17-18")
school_file = open("../universities/UCI/UCI.info")
debug = True
""""""
# will load info from the major/school files, make objects with info from both file and course DB
try:

    courses_info = load_major_courses_into_data_structure(major_file, debug)
    school_vars = load_school_vars(school_file)
    if debug:
        printDebugInfo(courses_info, school_vars, major_file, school_file)
    major_file.close()
    school_file.close()


except Exception as e:
    print(str(e))
    print('We do not support this major at this University yet.')

# TODO: if script exits with anything but desired output to controller (PhP script or another),
# TODO(cont):"Say, 'Sorry, we do not support this yet.'"
# TODO put lines of code not in function into main function of this script

# TODO(IMPORTANT): Get this info passed in (probably in JSON)
# university
# major
# BS, BA, other types
# year_declared_under
# max units user prefers to take (if > than what school allows, school limit wins)
# specialization? y/n
#      if so, specialization = user_specialization
# is specific school needed? I prefer not for now
#



# OLD TESTING CODE

# institution = input("Institution: ")
# major = input("Major: ")
# BS_BA_Other = input("BS, BA or other?")
# year_declared_under = input("What year are you declaring under?")
# specialization = input("Do you have a specialization? (y/n)")
# if 'n' in specialization.lower():
#    specialization = None
# else:
#    specialization = input("What is your specialization?")
# build file path off of info
# try to get file, if not there 'Sorry, we don't support this yet'
# school_file, major_file = get_major_and_school_files(institution, major, BS_BA_Other, year_declared_under, specialization)
# school_file = get_school_file(insitution)
