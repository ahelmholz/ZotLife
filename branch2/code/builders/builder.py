from .combo_maker import make_combos
from multiprocessing import Process, Manager
import time

def build(runtime_vars):
    """Returns list of length runtime_vars['max_wanted_schedules'] containing working schedules"""
    feeder_pool = make_combos(runtime_vars)
    if runtime_vars['debug']:
        print('*** Feeder pool ***')
        print(feeder_pool)
        print('*** End feeder pool ***')

    # to make things easy
    builder_params = {
        # TODO: change -- pull from runtime_vars/user
        # for now things are hardcoded for implementing algorithm
        'start_build_from_year': 2018,
        'start_build_from_season' : 2,
        'seasons': {
            # leave_open_units is a list of lists [0] is # of units left open in that quarter, [1] is how many years of that quarter
            # e.g. [4,1] under 1 is leave 4 units open in one fall quarter
            # seasons are numbered for simplicity
            1: {'user_approved': True,
                     'max_units': 20,
                     'leave_open_units': [[4, 1], [2, 2]],
                     'max_quarters_left': 4 # can be used interchangeably
                     },
            2: {'user_approved': True,
                'max_units': 20,
                'leave_open_units': [[4, 1], [2, 2]],
                'max_quarters_left': 4  # can be used interchangeably
                },
            3: {'user_approved': True,
                'max_units': 20,
                'leave_open_units': [[4, 1], [2, 2]],
                'max_quarters_left': 4  # can be used interchangeably
                },
            4: {'user_approved': False,
                'max_units': 20,
                'leave_open_units': [[4, 1], [2, 2]],
                'max_quarters_left': 4  # can be used interchangeably
                }
        }
    }
    manager = Manager()
    schedules = manager.dict()
    builder_timeout = 15 # CHANGE_VAR -- seconds
    start = time.time()
    i = 0
    while time.time() - start < builder_timeout and len(schedules) < runtime_vars['max_wanted_schedules'] and \
                    i < len(feeder_pool):
        p1 = Process(target=build_schedules, args=(feeder_pool[i], schedules, builder_params, runtime_vars, builder_timeout,))
        if i + 1 < len(feeder_pool):
            p2 = Process(target=build_schedules, args=(feeder_pool[i +1], schedules, builder_params, runtime_vars, builder_timeout,))
        p1.start()
        if i + 1 < len(feeder_pool):
            p2.start()
        p1.join()
        if i + 1 < len(feeder_pool):
            p2.join()
        i += 2

    # AFTER working schedules are built, pool info for those courses from DB for level 2 sorting
    # NOTE:
        # level 1: Courses
        # level 2: Individual classes/labs/discussions
    # TODO: add option to move courses back in case user doesn't pass a course (functionality may be somewhere else)
def add_blackouts(entry, blackouts):
    temp = 0
    for i in range(len(blackouts)):
        if blackouts[i][1] > 0:
            temp = blackouts[i][0]
            blackouts[i][1] -= 1
            break
    entry['blacked_out'] = temp

def build_schedules(input, schedules, builder_params, runtime_vars, timeout):
    start = time.time()
    starting_frame = {}
    max_left = 0
    start_year = builder_params['start_build_from_year']
    start_season = builder_params['start_build_from_season']
    # get max years
    for key in builder_params['seasons']:
        if builder_params['seasons'][key]['max_quarters_left'] > max_left:
            max_left = builder_params['seasons'][key]['max_quarters_left']
    for i in range(max_left):
        starting_frame[start_year + i] = {}
    for season in builder_params['seasons']:
        max_units = builder_params['seasons'][season]['max_units']

        if builder_params['seasons'][season]['user_approved']:
            for year in starting_frame:
                if year == start_year:
                    if season >= start_season:
                        starting_frame[year][season] = {'max_units': max_units, 'units_used': 0, 'courses': {}}
                        add_blackouts(starting_frame[year][season],
                                      builder_params['seasons'][season]['leave_open_units'])
                else:
                    starting_frame[year][season] = {'max_units': max_units, 'units_used': 0, 'courses': {}}
                    add_blackouts(starting_frame[year][season], builder_params['seasons'][season]['leave_open_units'])
    # TODO move blackouts if needed
    # TODO move coreqs together
    if runtime_vars['debug']:
        # NOTE: this will be printed for each process
        print('**** STARTING SCHEDULE FRAME ****')
        print(starting_frame)
        print('**** END ****')

    # pre-populate with needed blocks
    # use a stack to avoid function call overhead
    while time.time() - start < timeout and len(schedules) < runtime_vars['max_wanted_schedules']:
        # TODO implement
        # TODO check time to prevent loop from taking longer than allotted 
        pass

