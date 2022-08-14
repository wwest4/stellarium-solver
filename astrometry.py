import os
from multiprocessing import Process
from subprocess import run, PIPE, STDOUT
from time import time

astrometry_install_dir = '/usr/local/astrometry'

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


def _astrometry_solver(filename, location):
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
    exec_and_args = [solver_bin] + solver_args
    exec_string = ' '.join(exec_and_args)

    # deactivate venv temporarily
    venv, path = _deactivate_venv()

    print(f'executing: {exec_string}')
    solve_start = time()
    run(exec_and_args, stdout=PIPE, stderr=STDOUT)
    solve_finish = time()
    print(f'solver halt after {solve_finish - solve_start} sec')

    # reactivate venv
    _reactivate_venv(venv, path)


def solver(filename, location):
    p = Process(target=_astrometry_solver, args=(filename, location,))
    p.start()
    p.join()
