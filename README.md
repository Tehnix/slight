slight
======

Super Light Irresistible GitHub Tool... You know, like jenkins, only super light...

First, you'll need the yaml module, which you can get via `pip install PyYaml`.

* Set the GitHub webhook to `http://you_server:13373`.
* Make a shell script called `scripts/githubUsername_repositoryName`
* A config file is later coming to allow several tweaks...

Lastly, start the server with `python slight.py`.

### What? ###

Simply a server that listens to GitHub hooks sent in JSON. Once a hook is received, 
it then pulls the repository (if existent) and executes a shell script to deploy the project.

### Why? ###

We found that we used almost none of jenkins features, so, we made this little tool that 
will serve fine as a lightweight replacement.

### How? (With a bit more detail) ###

It's super easy to setup, you practically just set the webhook, and make a deploy script.

1) Make a webhook to your server by going into settings, under your repository, and choose webhook. Set the address to `http://you_server:13373`.

2) Then, make a shell script in the scripts folder which follows the naming convention `scripts/githubUsername_repositoryName`. This script must also have executable permission (chmod +x it), and a shebang line (`#!/bin/sh` or something).

3) A config file is later coming to allow several tweaks (when to send IRC messages, what branch to listen to, etc). The default is, at the moment, that it sends IRC messages for all steps, and, it only listens for a push to the master branch.

Start the server with `python slight.py`, and it'll listen to everything on port 13373.

### Get IRC messages ###

On the first run slight will create a file called `slight.yaml`. In here lies settings to make slight notify you about builds and such on IRC. It will set you up with an outcommented version, 
but, if you're a bit impatient, you can create your own settings file right away. The syntax looks 
like:

<pre>
irc:
    irc.freenode.net:
        port: 6697
        ssl: true
        channel: "#lobby"
        nickname: "slightCI"
</pre>

NOTE: A server *must* have all arguments assigned to it, else it will not get accepted (port, ssl, channel and nickname). You can have multiple servers by adding new ones under the other ones.
