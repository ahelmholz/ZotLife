class CourseWrapper:
    def __init__(self, number_to_pick=1):
        # check depth, can have multiple depths
        # check if type CourseWrapper or Course when doing work (nesting)
        self.number_to_pick = number_to_pick  # number needed to be taken out of group to meet requirement
        self.AND = []
        self.OR = []

    def __repr__(self):
        return '{}{}AND: {}, OR: {}{}'.format(self.number_to_pick, '{', self.AND, self.OR, '}')

