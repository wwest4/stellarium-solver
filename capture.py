import re
import os

from os import listdir, stat
from os.path import exists, isfile, getmtime
from pathlib import Path
from shutil import copy2 as copy
from time import sleep, time


home_dir = os.environ["HOME"]
solver_cache_dir = f'{home_dir}/.solver'

file_age_limit_s = 60
poll_rest_interval_s = 1


def poll_for_file():
    print("watching for new images...")
    while True:
        result = _asi_poll_for_file()
        if result:
            return result
        else:
            sleep(poll_rest_interval_s)


def _file_age_s(full_path):
    return time() - getmtime(full_path)


def _asi_poll_for_file():
    # match on a pattern
    home_dir = os.environ['HOME']
    scan_dir = f'{home_dir}/ASIImg'
    pattern = re.compile(r'^Preview_.*.fit$')

    Path(solver_cache_dir).mkdir(exist_ok=True)

    # sort by reverse mtime to ensure the latest files are found first
    files = sorted(listdir(scan_dir), key=lambda f: stat(f'{scan_dir}/{f}').st_mtime, reverse=True)

    for file_name in files:
        full_path = f'{scan_dir}/{file_name}'
    
        if(isfile(full_path)
                and _file_age_s(full_path) < file_age_limit_s
                and re.match(pattern, file_name)):
            dst_path = f'{solver_cache_dir}/{file_name}'
            if not exists(dst_path):
                copy(full_path, dst_path)
            else:
                # touch cached copy to hint at solver to reset expiration timer
                Path(dst_path).touch(exist_ok=True)

            return dst_path
