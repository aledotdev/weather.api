import fabtools, json, os
from fabric.api import env, roles

import utils

def load_config(env_type):

    with open("settings/%s.json" % env_type) as ff:
        conf = json.loads(ff.read())

    env.roledefs = conf['roledefs']

    app_path = conf['app']['path']
    conf['app']['path_src'] = os.path.join(app_path, 'src')
    conf['app']['path_venv'] = os.path.join(app_path, 'venv')
    conf['app']['path_logs'] = os.path.join(app_path, 'logs')

    env.app = conf['app']
    env.venv_python = os.path.join(conf['app']['path_venv'], 'bin', 'python')
    env.venv_pip = os.path.join(conf['app']['path_venv'], 'bin', 'pip')

@roles('app')
def base_setup():

    fabtools.require.deb.uptodate_index(quiet=True, max_age=dict(day=1))
    utils.setup_base()
    utils.require_app_user()
    utils.require_app()
    utils.update_app()

@roles('app')
def update_app():
    utils.update_app()

load_config('local')