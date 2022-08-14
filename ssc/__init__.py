import json
import os
import requests

from jinja2 import Environment, PackageLoader, select_autoescape
from os import listdir
from urllib.parse import urlencode

rc_ssc_api_base = 'http://localhost:8090/api/scripts'

template_args = {
        'current_location.ssc.jinja': {
            'output_filename': 'current_location.json',
        },
        'snap_to_solver.ssc.jinja': {
            'ra': '00h 42m 44s',
            'dec': '41d 16m 9s',
            'rotation_angle': 30,
            'zoom_arc_min': 6,
            'output_filename': 'snap_to_solver.json',
        },
}


def _build_function(template):
    def f(args_override=None):
        # get args and merge user overrides
        script_args = template_args.get(template.name, {})
        if args_override:
            script_args = {**script_args, **args_override}
        ssc = template.render(**script_args)

        # invoke the ssc against the RC API
        data = {'code': ssc}
        response = requests.post(f'{rc_ssc_api_base}/direct', data=data)

        # grab output
        output_filename = script_args['output_filename']
        home_dir = os.environ.get("HOME")
        with open(f'{home_dir}/.stellarium/{output_filename}') as output_file:
            output = output_file.read()
            return json.loads(output)

        raise RuntimeException("failed to invoke ssc from template {template.name}")

    return f


def _strip_suffix(filename):
    return '.'.join(filename.split('.')[0:-1]) 


def _templates_to_functions():
    env = Environment(
        loader=PackageLoader("ssc"),
        autoescape=select_autoescape()
    )

    ssc_template_files = [e for e in os.listdir(f'./ssc/templates/') if e.endswith('.ssc.jinja')]
    ssc_templates = [env.get_template(f) for f in ssc_template_files]

    script_functions = {}
    for template in ssc_templates:
        # remove trailing suffix
        script_name = _strip_suffix(template.name)
        script_functions[script_name] = _build_function(template)

    return script_functions


for script_name, function in _templates_to_functions().items():
    function_name = _strip_suffix(script_name)
    locals()[function_name] = function
