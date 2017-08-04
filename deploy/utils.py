import os, fabtools as ft
from fabric.api import settings, put, env, sudo, output, cd, run, prefix
from fabric.contrib import files


def setup_base():
    ft.require.deb.packages(['redis-server', 'nginx', 'supervisor', 'git'])


def require_app_user():
    user = env.app['user']
    ft.require.users.user(user)
    with settings(sudo_user=env.app['user']):
        home = ft.user.home_directory(user)

        ssh_path = os.path.join(home, '.ssh')
        ft.require.files.directory(ssh_path, use_sudo=True)
        ft.user.add_host_keys(user, 'bitbucket.org')

        run('git config --global user.email "test@test.com"')
        run('git config --global user.name test')

    ft.require.files.file(os.path.join(ssh_path, 'id_rsa.pub'),
                          source="templates/ssh.key.pub",
                          use_sudo=True, owner=user, group=user)
    ft.require.files.file(os.path.join(ssh_path, 'id_rsa'),
                          source="templates/ssh.key", use_sudo=True,
                          owner=user, group=user, mode="0600")


def require_app():
    app_user = env.app['user']
    ft.require.deb.packages(['python-dev', 'python-virtualenv'])
    ft.require.files.directory(env.app['path'], use_sudo=True, owner=app_user,
                               group=app_user)

    with settings(sudo_user=app_user):
        ft.require.files.directory(env.app['path_logs'], use_sudo=True)
        ft.require.python.virtualenv(env.app['path_venv'], use_sudo=True)
        ft.require.git.working_copy(env.app['repo'], env.app['path_src'],
                                    use_sudo=True)

    require_supervisor()
    require_nginx()


def update_app():
    ft.require.deb.packages(['libcurl4-gnutls-dev'])
    with settings(sudo_user=env.app['user']):
        ft.fabtools.git.pull(env.app['path_src'], force=True, use_sudo=True)
        reqs_file = os.path.join(env.app['path_src'], 'requirements.txt')
        pip_cmd = 'HOME="/home/weatherapi/" %s' % env.venv_pip
        ft.python.install_requirements(reqs_file, pip_cmd=pip_cmd,
                                       use_sudo=True)

    restart_app()


def require_nginx():
    server_list = []
    for port in env.app['ports']:
        server_list.append('server localhost:%s;' % port)

    CONFIG_TPL = '''
    upstream %(app_name)s {
        %(server_list)s
    }
    server {
        listen      %(port)d;
        client_max_body_size 50M;
        server_name %(server_name)s;

        location / {
            proxy_pass_header Server;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Scheme $scheme;
            proxy_pass http://%(app_name)s;
        }
    }'''

    ft.require.nginx.site(env.app['server_name'],
        template_contents=CONFIG_TPL,
        server_list="\n\t\t".join(server_list),
        port=env.app['nginx_port'],
        app_name=env.app['name']
    )

    ft.require.nginx.disabled('default')
    ft.require.nginx.enabled(env.app['server_name'])
    ft.service.reload('nginx')


def require_ssh_credentials():
    ft.require.files.directory(SSH_PATH)
    ft.require.files.file(path.join(SSH_PATH, 'id_rsa'),
                          source="templates/sshkey.envs", mode="0600")
    ft.require.files.file(path.join(SSH_PATH, 'config'),
                          source="templates/ssh.conf")


def require_supervisor():
    for port in env.app['ports']:
        ft.require.supervisor.process(
            get_app_supervisor_name(port),
            command='%s %s/weatherapi/run.py --port=%s' % (env.venv_python, env.app['path_src'], port),
            directory=os.path.join(env.app['path_src'], 'src'),
            user=env.app['user'],
            stdout_logfile=os.path.join(env.app['path_logs'], 'app.log'),
            environment='ENV="dev"'
        )

    ft.supervisor.reload_config()


def get_app_supervisor_name(port):
    return 'weather.api.%s' % port


def restart_app():
    for port in env.app['ports']:
        ft.supervisor.restart_process(get_app_supervisor_name(port))
