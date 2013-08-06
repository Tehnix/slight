slight
======

Super Light Irresistible GitHub Tool... You know, like jenkins, only super light...

### What? ###

Simply a server that listens to GitHub hooks sent in JSON. Once a hook is received, 
it then pulls the repository (if existent) and executes a shell script to deploy the project.

### Why? ###

We found that we used almost none of jenkins features, so, we made this little tool that 
will serve fine as a lightweight replacement.

### How? ###

Admittedly, the initial setup of a project requires a little work. A little.

1) First, you go clone the repository you want into the repos folder. It should be as such `repos/githubUsername/repositoryName`. Where, of course, `githubUsername` is replaced by the owner of the repository you cloned, and `repositoryName` is replaced by, obviously, the repository name.

2) You then make a shell script in the scripts folder which follows the naming convention `scripts/githubUsername_repositoryName`. This script must also have executable permission (chmod +x it), and a shebang line (`#!/bin/sh` or something).

3) A config file is later coming to allow several tweaks (when to send IRC messages, what branch to listen to, etc). The default is, at the moment, that it sends IRC messages for all steps, and, it only listens for a push to the master branch.

