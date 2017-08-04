''' This will make sense later -- MUCH thought has gone into it and it is probably really confusing without implementation '''
class PrereqWrapper:
    def __init__(self):
        # check depth, can have multiple depths
        # check if type PrereqWrapper or Course when doing work (nesting)
        self.AND = []
        self.OR = []
        
    def __repr__(self):
        return '[AND: {}, OR: {}]'.format(self.AND, self.OR)

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

    def add_var(self, var, val):
        self.variables[var] = val

    def add_comment(self, comment):
        self.comment = comment

    def add_prereq(self, course_obj):
        self.prereqs.append(course_obj)

    def __str__(self):
        return 'Course name: {}\n\tvars: {}\n\tcomment: {}\n\tprereq_list: {}\n\tpreq_for_list: {}'.format(
            self.course_name, self.variables, self.comment, self.prereqs, self.is_prereq_for)

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

def check_basic_syntax_and_remove_comments(major_file):

    def print_error(line_num):
        print('An error occurred while parsing major file at line {}. Exiting...'.format(line_num))
        exit()

    ret_string = ''
    special_comment = ''
    open_square_count = 0
    open_par_count = 0
    line_number = 0
    for line in major_file:
        line_number += 1
        ignore_rest_of_line = False
        for char in line:
            if not ignore_rest_of_line:
                if char == '#':
                    ignore_rest_of_line = True
                else:
                    if "'''" in line:
                        special_comment += line
                        break
                    elif char == '[':
                        open_square_count += 1
                    elif char == ']':
                        open_square_count -= 1
                        if open_square_count < 0:
                            print_error(line_number)
                    elif char == '(':
                        open_par_count += 1
                    elif char == ')':
                        open_par_count -= 1
                        if open_par_count < 0:
                            print_error(line_number)
                    # add char to ret_object
                    ret_string += char
            else:
                if char == '\n':
                    ret_string += char
                    ignore_rest_of_line = False
    if open_square_count > 0 or open_par_count > 0:
        print_error(-1)
    # remove quotes from special comment
    special_comment = special_comment.replace("'''", "").strip()
    return (special_comment, ret_string.strip())

# stores info from both .maj file and class database
def load_major_courses_into_data_structure(major_file):

    # put courses in dictionary for loading all info easily and efficiently
    # will make objects from below
    course_dict = {}

    # will be a tuple, the first string being the comment to the user about the major, the second being the remaining text
    major_strings = check_basic_syntax_and_remove_comments(major_file)
    #print(major_strings[1])
    # at this point, ''' ''' and # are stripped, somewhat valid parenthesis have been checked for

    # split lines into two -- first half is major outline -- second half is course requirements
    expression = ''
    expression_terminatied = False
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
        local_expression_terminated = False
        # skipping first line which was course to open
        for line in course.splitlines()[1:]:
            if '\\' in line.strip()[-1:]:
                local_expression_terminated = False
                local_expression += line[0:-1]
            else:
                local_expression_terminated = True
                local_expression += line
            if local_expression_terminated:
                # process expression here
                # is var?
                if '=' in line:
                    temp = line.split('=')
                    working_course.add_var(temp[0].strip(), temp[1].strip())
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
                        # TODO: WORKING HERE - what is prereq course
                        pass
                course_dict[working_course.course_name] = working_course
                local_expression = ''
    ###
    for key, val in course_dict.items():
        print(val)
        print()
    ###

    # add to course if it is required
    # add to coreqs?
    # process major requirements
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
except:
    print('We do not support this major at this University yet.')