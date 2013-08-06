slight
======

Super Light Irresistable GitHub Tool... You know, like jenkins, only super light...

## What? ##

Simply a server that listens to GitHub hooks sent in JSON. Once a hook is received, 
it then pulls the repository (if existent) and executes a shell script to deploy the project.

## Why? ##

We found that we used almost none of jenkins features, so, we made this little tool that 
will serve fine as a lightweight replacement.