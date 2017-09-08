from .combo_maker import make_combos

def build(runtime_vars):
    """Returns list of length runtime_vars['max_wanted_schedules'] containing working schedules"""
    feeder_pool = make_combos(runtime_vars)
    if runtime_vars['debug']:
        print('*** Feeder pool ***')
        print(feeder_pool)
        print('*** End feeder pool ***')

    # # if course has co-req, move together in schedule building

    # AFTER working schedules are built, pool info for those courses from DB for level 2 sorting
    # NOTE:
        # level 1: Courses
        # level 2: Individual classes/labs/discussions

    # TODO: allow slots for other courses
    # TODO: add option to move courses back in case user doesn't pass a course (functionality may be somehwere else)




