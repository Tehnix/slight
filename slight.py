import sys
import json
import urllib2
import BaseHTTPServer
import SimpleHTTPServer
import subprocess
import threading

#import irc_bot


class MyHTTPServer(BaseHTTPServer.HTTPServer):
    allow_reuse_address = True


class MyHTTPServerHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    locks = {}
    
    @staticmethod
    def get_lock(cls, ident):
        return MyHTTPServerHandler.locks.get(ident, threading.Semaphore())
    
    def do_POST(self):
        content_len = int(self.headers.getheader('content-length'))
        post_body = self.rfile.read(content_len)
        if post_body.startswith("payload"):
            json_payload = json.loads(urllib2.unquote(post_body[8:]))
            data = parse(json_payload)
            ident = '{0}/{1}'.format(data["name"], data["repo_name"])
            thread = threading.Thread(target=handle_hook, args=(ident, data))
            thread.start()

def handle_hook(ident, data):
    # Only execute on push to master
    sem = MyHTTPServerHandler.get_lock(ident)
    sem.acquire()
    if data is not None and data["refs"] == "refs/heads/master":
        git_update(data)
        execute_shell_script(data)
    sem.release()

def parse(json):
    try:
        repo_name = json["repository"]["name"]
        owner_name = json["repository"]["owner"]["name"]
        push_name = json["pusher"]["name"]
        commits = len(json["commits"])
        refs = json["refs"]
    except IndexError:
        return None
    else:
        return {
            "name": owner_name, "repo_name": repo_name,
            "push_name": push_name, "commits": commits,
            "refs": refs
        }

def git_update(data):
    notify('Hook received by `{0}` for `{1}/{2}`, performing pull...'.format(
        data["push_name"], data["name"], data["repo_name"]
    ))
    # perform git pull here
    notify('!!!!!!!!!! --> git pull not implemented yet! <-- !!!!!!!!!!!!')
    notify('Updated `{0}/{1}` with {2} commits!'.format(
        data["name"], data["repo_name"], data["commits"]
    ))
    

def execute_shell_script(data):
    script = './{0}_{1}'.format(data["name"].lower(), data["repo_name"].lower())
    try:
        notify('Starting job for `{0}/{1}`'.format(data["name"], data["repo_name"]))
        subprocess.call([script])
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

def notify(msg):
    print msg


if __name__ == "__main__":
    httpd = MyHTTPServer(('', 13373), MyHTTPServerHandler)
    httpd.serve_forever()
