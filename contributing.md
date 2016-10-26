Contributing
============
Contributions are most welcome, post bug fixes, new features, anything you'd like want to see.
Note that, for example, replacing the text control with a STCWindow wouldn't be accepted (most likely), as it's accessibility is quite poor, if any. But if you hide the accessibility degrading changes under an option, i have no problems with that.

Updating translations
---------------------
I know, the procedure should have been automated long time ago, but it is basically as follows
- Run scripts/extract_strings_from_xrc.py ui.xrc
- Then run xgettext --from-code utf-8 *.py
- If you are starting a new language, copy the messages.po file to locale/<lang>/LC_MESSAGES and translate it, followed by a .mo generation.
- Otherwise, run msgmerge -U locale/<lang>/LC_MESSAGES/messages.po messages.po
- Then, you should remove the ui_strings.py, messages.po and messages.po~ fin your lang subdirectory.