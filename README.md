slight
======

First off, you'll need the yaml module, which you can get via `pip install PyYaml`.

* Set the GitHub webhook to `http://you_server:13373`.
* Make a shell script called `scripts/githubUsername_repositoryName`
* A config file is later coming to allow several tweaks...

Lastly, start the server with `./slight.py start`.

NOTE: On the first run of the program, it'll create a settings file called `settings.yaml`. This is, for now, only used for the IRC bot settings, so, if you don't need this, just ignore it, and rerun the program.

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

Start the server with `./slight.py start`, and it'll listen to everything on port 13373.

### Dependencies ###

The goal is to have as little dependicies on things outside the standard library. Alas, alas, some may have gotten through the needle-eye.

List of needed modules/packages:
* `yaml` which can be installed with `pip install PyYaml`

### Get IRC messages ###

On the first run slight will create a file called `slight.yaml`. In here lies settings to make slight notify you about builds and such on IRC. It will set you up with an out-commented version, 
but, if you're a bit impatient, you can create your own settings file right away. The syntax looks 
like:

<pre>
irc:
    operator: "!"
    enabled: true
    FreeNode:
        server: irc.freenode.net:
        port: 6697
        ssl: true
        channel: "#lobby"
        nickname: "slight-ci"
    FreeNodeAlt:
        server: irc.freenode.net:
        port: 6697
        ssl: true
        channel: "#slight"
        nickname: "slight-ci"
</pre>

A server only needs the `server`, `channel` and `port` arguments. You can have multiple servers by adding new ones under the other ones.

NOTE: You must have `enabled` set to true for the IRC bots to get started. You can, of couse, also just disable them by setting it to false.
