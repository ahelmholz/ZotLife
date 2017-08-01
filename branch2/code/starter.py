def get_major_file(institution, major, type, catalog_year, specialization=None):
    # basic checks of input to function -- won't catch everything (should be done elsewhere)
    # NOTE: revise tests?
    if not institution.isupper():
        print('Error 1 in get_major_file')
        exit()
    # NOTE: type will have to change later to include grad degrees/minors?
    if len(type) != 2 or (type != 'BS' and type!='BA'):
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

# stores info from both .maj file and class database
def load_major_courses_into_data_structure(major_file):
    # put courses in dictionary for loading all info easily and efficiently
    # will make objects from below
    course_dict = {}

    # logically..Not actually
    square_brace_stack = 0
    """   WORK IN PROGRESS """
    for line in major_file:
        # build quote if there
        # open working 'class' with methods to add to it until over
        for char in line:
            if char == '#':
                break
            elif char == '[':
                square_brace_stack += 1
            elif char == ']':
                # more ']' than '['
                square_brace_stack -= 1
                if square_brace_stack < 0:
                    print("The syntax in the specified major file is incorrect")
                    exit()


    # define what needs to be returned
    # return the courses here
    """"""""""""""""""""""""""
    return True

''' This will make sense later -- MUCH thought has gone into it and it is probably really confusing without implementation '''

# VERY powerful because it combines major info with specific, up to date class info for filtering
class Course:
    def __init__(self):
        self.isRequiredByMajor = None # since dict will be initialized with all prereqs as well
        self.user_has_taken = None
        # preqs before course
        self.prereq_wrapper = None
        self.coreq_list = []
        # what is this class a prereq for?
        self.course_is_prereq_for = None
        # wrapper to say which courses have to be taken(AND/OR)
        # pull/store info from DB?
        # when is it offered?


class PrereqWrapper:
    def __init__(self):
        # check depth, can have multiple depths
        # check if type PrereqWrapper or Course when doing work (nesting)
        AND = []
        OR = []

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
courses = load_major_courses_into_data_structure(major_file)