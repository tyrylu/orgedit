Org Editor
==========
This application is an accessible note taking utility. As it's file format it uses the org file format as used by the org-mode Emacs major mode.

Why not use Emacs directly?
---------------------------
Emacs can be configured to talk nicely under Linux, but under Windows, the situation is worse (non-standard e.g. arrow based cursor move commands aren't spoken, the echoed messages as well etc.).

Goals
-----
This project is there to provide a feature rich note taking application, taking accessibility into accord.
Thus, it will try to implement as many useful features as possible.

System requirements
------------
The program requires WxPython 3.x (not tested with older releases). In theory, it should work under Wxpython Phoenix under Python 3, but unfortunately, under Windows at least, it throws an access violation after start. Thus, Python 2.x is now required, apologies.

Getting it and using
----------
Just clone the repository, or download a archive and run main.py.