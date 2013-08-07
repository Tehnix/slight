#!/usr/bin/env python
"""
The slight server listens to JSON POST requests from Githubs webhooks.

Once a webhook is recieved, a thread is started that pulls down the updates,
and after that, it executes a deploy/shell script.

It's also able to notify about the progress in IRC channels, via the irc module.

"""
import os
import subprocess
import threading
import urllib2
import BaseHTTPServer
import json
import logging
import time

from constants import BASE_PATH
from irc.messages import notify


rel = lambda path: BASE_PATH + os.sep + os.sep.join(path)


class MyHTTPServer(BaseHTTPServer.HTTPServer):
    """Light HTTP server."""
    allow_reuse_address = True


class MyHTTPServerHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Handle HTTP requests."""
    semaphores = {}
    
    @staticmethod
    def get_semaphore(ident):
        """Return the semaphore for the repository."""
        return MyHTTPServerHandler.semaphores.get(ident, threading.Semaphore())
    
    def do_POST(self):
        """Handle POST requests."""
        content_len = int(self.headers.getheader('content-length'))
        post_body = self.rfile.read(content_len)
        if post_body.startswith("payload"):
            json_payload = json.loads(urllib2.unquote(post_body[8:]))
            data = parse(json_payload)
            ident = '{0}/{1}'.format(data["name"], data["repo_name"])
            thread = threading.Thread(target=handle_hook, args=(ident, data))
            thread.daemon = True
            thread.start()

def run_server():
    """Run the HTTP server."""
    logging.info("Starting HTTP Server...")
    httpd = MyHTTPServer(('', 13373), MyHTTPServerHandler)
    httpd.serve_forever()

def parse(json_payload):
    """Parse the received JSON and return a dict of the valuable information."""
    try:
        repo_name = json_payload["repository"]["name"]
        owner_name = json_payload["repository"]["owner"]["name"]
        push_name = json_payload["pusher"]["name"]
        commits = str(len(json_payload["commits"]))
        ref = json_payload["ref"]
        url = json_payload["repository"]["url"]
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
    logging.info("Handling hook for `{0}/{1}`".format(data["name"], data["repo_name"]))
    # Only execute on push to master
    with MyHTTPServerHandler.get_semaphore(ident):
        if data is not None and data["ref"] == "refs/heads/master":
            check_repository_existence(data)
            git_update(data)
            execute_shell_script(data)

def check_repository_existence(data):
    """
    Check if a repository exists (and the subsequent owner), else, clone
    down the repository from the url received with the hook.
    
    """
    logging.info("Checking if repository `{0}/{1}` exists...".format(
        data["name"], data["repo_name"]
    ))
    repo_dir = rel(['repos', data["name"], data["repo_name"]])
    if not os.path.isdir(repo_dir):
        notify('Cloning `{0}/{1}`...'.format(data["name"], data["repo_name"]))
        with open(os.devnull, 'w') as devnull:
            subprocess.Popen(
                [
                    'git', 'clone', data["url"], 
                    os.sep.join(['repos', data["name"], data["repo_name"]])
                ],
                cwd=BASE_PATH, stdout=devnull, stderr=devnull
            )
    
def git_update(data, queue=None):
    """Perform a git pull in the repository."""
    repo_dir = 'repos/{0}/{1}'.format(data["name"], data["repo_name"])
    with open(os.devnull, 'w') as devnull:
        subprocess.Popen(
            ['git', 'pull', 'origin', 'master'],
            cwd=repo_dir, stdout=devnull, stderr=devnull
        )
        subprocess.Popen(
            ['git', 'submodule', 'init'],
            cwd=repo_dir, stdout=devnull, stderr=devnull
        )
        subprocess.Popen(
            ['git', 'submodule', 'update'],
            cwd=repo_dir, stdout=devnull, stderr=devnull
        )
    notify('Pulled down {2} commit(s) for project `{0}/{1}`'.format(
        data["name"], data["repo_name"], data["commits"]
    ), queue)
    
def execute_shell_script(data, queue=None):
    """Execute the accompanying shell/deploy script for the repo."""
    script = '{0}_{1}'.format(
        data["name"].lower(), data["repo_name"].lower()
    )
    script_path = rel(['scripts', script])
    if os.path.exists(script_path):
        try:
            notify('Starting build for job `{0}/{1}`'.format(
                data["name"], data["repo_name"]
            ), queue)
            start = time.time()
            with open(os.devnull, 'w') as devnull:
                subprocess.Popen(
                    ['./{0}'.format(script)],
                    cwd=script_path, stdout=devnull, stderr=devnull
                )
            end = time.time() - start
            notify('Project `{0}/{1}` build in {2}'.format(
                data["name"], data["repo_name"]
            ), queue)
        except OSError, excep:
            exception = str(excep)
            if exception.startswith('[Errno 2]'):
                notify('No script to execute. Please create one first!', queue)
            elif exception.startswith('[Errno 13]'):
                notify('The script is not executable!', queue)
            elif exception.startswith('[Errno 8]'):
                notify('Format error with the script!', queue)
            else:
                notify('Uncaught error, calling script: {0}'.format(exception), queue)
                logging.exception("Job for `{0}/{1}` threw an exception".format(
                    data["name"], data["repo_name"]
                ))
    else:
        notify('Project `{0}/{1}` build in {2}'.format(
            data["name"], data["repo_name"]
        ), queue)
        notify('No build script found for job `{0}/{1}`'.format(
                data["name"], data["repo_name"]
            ), queue)
