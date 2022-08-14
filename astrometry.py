import os

from collections import namedtuple
from multiprocessing import Process, Queue
from os.path import exists
from subprocess import run, PIPE, STDOUT
from time import sleep, time


astrometry_install_dir = '/usr/local/astrometry'


def solver(filename, location):
    queue = Queue()

    process = Process(target=_astrometry_solver, args=(filename, location, queue,))
    process.start()
    process.join()

    solution = queue.get()
    if solution:
        SolverSolution = namedtuple('SolverSolution', solution.keys())
        return SolverSolution(**solution)

    return None


def wcsinfo_parse(wcsinfo_output):
    lines = wcsinfo_output.decode('UTF-8').splitlines()
    solution = {}

    for line in lines:
        key, value = line.split(' ')
        solution[key] = value

    return solution


def astrometry_to_stellarium_ra(astrometry_ra):
    """ from: '01:54:54.240'
          to: '00h 42m 44s'
    """
    hour, minute, second = astrometry_ra.split(':')
    return f'{hour}h {minute}m {second}s'


def astrometry_to_stellarium_dec(astrometry_dec):
    """ from: '+62:44:30.621'
          to: '41d 16m 9s'
    """
    degree, minute, second = astrometry_dec.split(':')
    return f'{degree}d {minute}m {second}s'


def _deactivate_venv():
    venv = os.environ.get('VIRTUAL_ENV', None)
    del os.environ['VIRTUAL_ENV']

    # strip venv dirs out of PATH
    path = os.environ.get('PATH')
    paths = path.split(':')
    new_paths = [p for p in paths if 'venv' not in p]
    os.environ['PATH'] = ':'.join(new_paths)

    # return original values
    return venv, path


def _reactivate_venv(venv, path):
    if venv:
        os.environ['VIRTUAL_ENV'] = venv
    os.environ['PATH'] = path

def _wcsinfo_exists(filename):
    return exists('.'.join(filename.split('.')[0:-1]) + '.wcs')
    

def _astrometry_solver(filename, location, queue):
    # TODO radius should probably be based on oculars settings/fov,
    #      though it's partially affected by operator skill; for now,
    #      just make it static + conservative
    radius_deg = str(30)
    ra = str(location['ra'])
    dec = str(location['dec'])

    solver_bin = f'{astrometry_install_dir}/bin/solve-field'
    solver_args = [
            '--guess-scale',
            '--no-plots',
            '--ra', ra,
            '--dec', dec,
            '--radius', radius_deg,
            filename,
    ]
    solver_exec_and_args = [solver_bin] + solver_args
    solver_exec_string = ' '.join(solver_exec_and_args)

    wcsinfo_bin = f'{astrometry_install_dir}/bin/wcsinfo'
    wcs_file_name = '.'.join(filename.split('.')[0:-1]) + '.wcs'
    wcsinfo_args = [wcs_file_name]
    wcsinfo_exec_and_args = [wcsinfo_bin] + wcsinfo_args
    wcsinfo_exec_string = ' '.join(wcsinfo_exec_and_args)

    # deactivate venv temporarily
    venv, path = _deactivate_venv()

    if not _wcsinfo_exists(filename):
        print(f'executing: {solver_exec_string}')
        solve_start = time()
        solver_result = run(solver_exec_and_args, stdout=PIPE, stderr=STDOUT)
        solve_finish = time()
        print(f'solver halt after {solve_finish - solve_start} sec')

        print(f'executing: {wcsinfo_exec_string}')
        wcsinfo_result = run(wcsinfo_exec_and_args, stdout=PIPE, stderr=STDOUT)
        parsed_wcsinfo = wcsinfo_parse(wcsinfo_result.stdout)
        print(f'wcsinfo parsed.')

        queue.put(parsed_wcsinfo)
    else:
        # cached solution found for this image, we probably are already done
        queue.put(None)

    # reactivate venv
    _reactivate_venv(venv, path)
