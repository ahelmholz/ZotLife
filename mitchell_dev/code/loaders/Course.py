class Course:
    def __init__(self, course_name):
        self.course_name = course_name
        self.variables = {}
        self.comment = ''
        # isRequiredOption means course is in major outline (may be optional -- but still in major outline)
        self.isRequiredOption = False  # since course_dict will be initialized with all prereqs as well
        self.user_has_taken = False  # False until True
        # preqs before course
        # list of Course and CourseWrapper objects
        self.prereqs = []
        self.coreq_list = []
        self.classes = []  # loaded from database
        # user can possibly take these courses after completing this course
        self.is_prereq_for = []
        # pull/store info from DB?
        # when is it offered?
        # TODO: add class info from DB -- only if course is in viable level 1 schedule
        self.percent_chance_offered = {}
        self.user_priority = None # Make priority system for scheduling (desired courses)

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
               'coreq_list: {}\n\tisRequiredOption: {}\n\tuser_has_taken: {}'.format(
            self.course_name, self.variables, self.comment, self.prereqs, self.is_prereq_for, self.coreq_list,
            self.isRequiredOption, self.user_has_taken)

    def __str__(self):
        return self.course_name

    def __repr__(self):
        return self.course_name

    def add_is_prereq_for(self, course):
        if course not in self.is_prereq_for:
            self.is_prereq_for.append(course)