slight
======

Super Light Irresistible GitHub Tool... You know, like jenkins, only super light...

* Clone the repository you want into `repos/githubUsername/repositoryName`
* Make a shell script called `scripts/githubUsername_repositoryName`
* A config file is later coming to allow several tweaks...

Lastly, start the server with `python slight.py`. And don't forget to set the GitHub webhook to `http://you_server:13373`.

### What? ###

Simply a server that listens to GitHub hooks sent in JSON. Once a hook is received, 
it then pulls the repository (if existent) and executes a shell script to deploy the project.

### Why? ###

We found that we used almost none of jenkins features, so, we made this little tool that 
will serve fine as a lightweight replacement.

### How? (With a bit more detail) ###

Admittedly, the initial setup of a project requires a little work. A little.

1) First, you go clone the repository you want into the repos folder. It should be as such `repos/githubUsername/repositoryName`. Where, of course, `githubUsername` is replaced by the owner of the repository you cloned, and `repositoryName` is replaced by, obviously, the repository name.

2) You then make a shell script in the scripts folder which follows the naming convention `scripts/githubUsername_repositoryName`. This script must also have executable permission (chmod +x it), and a shebang line (`#!/bin/sh` or something).

3) A config file is later coming to allow several tweaks (when to send IRC messages, what branch to listen to, etc). The default is, at the moment, that it sends IRC messages for all steps, and, it only listens for a push to the master branch.


The server itself doesn't depend on any libraries other than the ones from the std lib. Start the server with `python slight.py`, and it'll listen to everything on port 13373.

Also, make a webhook to your server by going into settings, under your repository, and choose webhook. Set the address to `http://you_server:13373`.

