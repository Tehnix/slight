import sys
import os
import subprocess
import threading
import urllib2
import BaseHTTPServer
import SimpleHTTPServer
import json
import yaml

import irc_bot


class MyHTTPServer(BaseHTTPServer.HTTPServer):
    allow_reuse_address = True


class MyHTTPServerHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    locks = {}
    
    @staticmethod
    def get_lock(ident):
        return MyHTTPServerHandler.locks.get(ident, threading.Semaphore())
    
    def do_POST(self):
        content_len = int(self.headers.getheader('content-length'))
        post_body = self.rfile.read(content_len)
        if post_body.startswith("payload"):
            json_payload = json.loads(urllib2.unquote(post_body[8:]))
            data = parse(json_payload)
            ident = '{0}/{1}'.format(data["name"], data["repo_name"])
            t = threading.Thread(target=handle_hook, args=(ident, data))
            t.start()

def run_server():
    httpd = MyHTTPServer(('', 13373), MyHTTPServerHandler)
    httpd.serve_forever()

def parse(json):
    """Parse the received JSON and return a dict of the valuable information."""
    try:
        repo_name = json["repository"]["name"]
        owner_name = json["repository"]["owner"]["name"]
        push_name = json["pusher"]["name"]
        commits = str(len(json["commits"]))
        ref = json["ref"]
        url = json["repository"]["url"]
    except IndexError:
        return None
    else:
        return {
            "name": owner_name, "repo_name": repo_name,
            "push_name": push_name, "commits": commits,
            "ref": ref, "url": url
        }

def handle_hook(ident, data):
    """
    Manage the different actions that need to be taken once a hook is received.
    Semaphores are used to make sure two pushs in quick succession doesn't happen
    simultaneously, but, rather sequentially.
     
    """
    # Only execute on push to master
    sem = MyHTTPServerHandler.get_lock(ident)
    sem.acquire()
    if data is not None and data["ref"] == "refs/heads/master":
        check_repository_existence(data)
        git_update(data)
        execute_shell_script(data)
    sem.release()

def check_repository_existence(data):
    """
    Check if a repository exists (and the subsequent owner), else, clone
    down the repository from the url received with the hook.
    
    """
    owner_dir = 'repos/{0}'.format(data["name"])
    if not os.path.isdir(owner_dir):
        os.mkdir(owner_dir)
    repo_dir = 'repos/{0}/{1}'.format(data["name"], data["repo_name"])
    if not os.path.isdir(repo_dir):
        notify('Cloning `{0}/{1}`...'.format(data["name"], data["repo_name"]))
        with open(os.devnull, 'w') as devnull:
            subprocess.Popen(
                ['git', 'clone', data["url"], repo_dir],
                stdout=devnull, stderr=devnull
            )
    
def git_update(data):
    """Perform a git pull in the repository."""
    notify('Hook received by `{0}` for `{1}/{2}`, performing pull...'.format(
        data["push_name"], data["name"], data["repo_name"]
    ))
    repo_dir = 'repos/{0}/{1}'.format(data["name"], data["repo_name"])
    with open(os.devnull, 'w') as devnull:
        subprocess.Popen(
            ['git', 'pull', 'origin', 'master'],
            cwd=repo_dir, stdout=devnull, stderr=devnull
        )
    notify('Updated `{0}/{1}` with {2} commits!'.format(
        data["name"], data["repo_name"], data["commits"]
    ))
    
def execute_shell_script(data):
    """Execute the accompanying shell/deploy script for the repo."""
    script = 'scripts/{0}_{1}'.format(data["name"].lower(), data["repo_name"].lower())
    if os.path.exists(script):
        try:
            notify('Starting job for `{0}/{1}`'.format(data["name"], data["repo_name"]))
            subprocess.call(['./{0}'.format(script)])
            notify('Done with job `{0}/{1}`!'.format(data["name"], data["repo_name"]))
        except OSError, e:
            if str(e).startswith('[Errno 2]'):
                notify('No script to execute. Please create one first!')
            elif str(e).startswith('[Errno 13]'):
                notify('The script is not executable!')
            elif str(e).startswith('[Errno 8]'):
                notify('Format error with the script!')
            else:
                notify('Uncaught error, calling script: {0}'.format(str(e)))
    else:
        notify('No script to execute. Please create one first!')

def notify(msg):
    irc_bot.add_to_queue(msg)
    print ">>> {0}".format(msg)

def create_first_settings_file():
    if not os.path.exists('slight.conf'):
        with open('slight.conf', 'w') as conf:
            conf.write("\n".join([
                "# -- Example of usage --",
                "#irc:",
                "#    irc.freenode.net:",
                "#        port: 6697",
                "#        ssl: true",
                "#        channel: \"#lobby\"",
                "#        nickname: \"slight-ci\""
            ]))

def check_settings_validity():
    with open('slight.conf', 'r') as conf:
        settings = yaml.safe_load(conf)
        irc = settings.get('irc')
        if settings is not None and irc is not None:
            for server, info in irc.items():
                if info.get('port') is None or info.get('ssl') is None or info.get('channel') is None or info.get('nickname') is None:
                    print "Invalid slight.conf file. nickname, port, ssl and channel must be set!"
                    return False
                return True
    return None

def fetch_irc_servers_from_settings():
    with open('slight.conf', 'r') as conf:
        settings = yaml.safe_load(conf)
        return settings.get('irc')

if __name__ == "__main__":
    create_first_settings_file()
    check_settings = check_settings_validity()
    if check_settings and check_settings is not None:
        servers = fetch_irc_servers_from_settings()
        irc_bot.start_irc_bot(servers)
    if check_settings or check_settings is None:
        t = threading.Thread(target=run_server)
        t.start()
        t.join()
