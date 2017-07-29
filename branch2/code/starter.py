
""" JUST FOR TESTING """
institution = input("Institution: ")
major = input("Major: ")
BS_BA_Other = input("BS, BA or other?")
year_declared_under = input("What year are you declaring under?")
specialization = input("Do you have a specialization? (y/n)")

# get classes already taken

""""""

# build file path off of info
# try to get file, if not there 'Sorry, we don't support this yet'
major_file = get_major_file()

# will load info from the major file, instansiate objects with info from both file and course DB
load_major_courses_into_data_structure()

def get_major_file():
    return True

# stores info from both .maj file and class database
def load_major_courses_into_data_structure(major_file):
    """ """
    # put courses in dictionary for loading all info easily and efficiently
    # will make objects from below
    course_dict = {}


    # define what needs to be returned
    # return the courses here
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

