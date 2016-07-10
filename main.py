import sys
import os
import wx
app = wx.App()
# It must be done before any app level imports, excuse me.
# Locale setup, including the __builtins__ hack similar to the gettext.install's one.
locale = wx.Locale(wx.LANGUAGE_DEFAULT)
locale.AddCatalogLookupPathPrefix(os.path.join(os.path.dirname(sys.argv[0]), "locale"))
locale.AddCatalog("messages")
if int(sys.version[0]) >= 3:
    import builtins
else:
    import __builtin__ as builtins
builtins.__dict__['_'] = locale.GetString

import main_frame
import uimanager
frame = main_frame.MainFrame()
mgr = uimanager.UIManager("ui.xrc", "mainwindow", reuse_app=True, load_on=frame)
mgr.auto_bind(mgr.top_level, mgr.top_level, alternate_bind_of=["on_tree_tree_sel_changed"])
mgr.top_level.Bind(wx.EVT_CLOSE, mgr.top_level.on_quit_selected) # Needed, window event binding is a third way of binding unsupported by UiManager
        
if len(sys.argv) == 2:
    mgr.top_level.open_file(sys.argv[1])
else: # New file
    mgr.top_level.create_new_file()
mgr.run()