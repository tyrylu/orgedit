Org Editor
==========
This application is an accessible note taking utility. As it's file format it uses the org file format as used by the org-mode Emacs major mode.

Why not use Emacs directly?
---------------------------
Emacs can be configured to talk nicely under Linux, but under Windows, the situation is worse (non-standard e.g. arrow based cursor move commands aren't spoken, the echoed messages as well etc.).

Goals
-----
This project is there to provide a feature rich note taking application, taking accessibility into accunt.
Thus, it will try to implement as many useful features as possible. Of course, .it will take some time.

System requirements
------------
The program requires Python 3.x (tested under 3.5) and Wxpython Phoenix.
And it also requires pysodium, which can be installing using pip, but note that pysodium requires the libsodium library to be somewhere on path.

Getting it
----------
Just clone the repository, or download an archive.

Usage
-----
It is really simple, just run main.py and enjoy.
You can pass the org file as an argument, so you should be able to create a system file type association, if you would like.