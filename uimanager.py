import wx
import wx.xrc as xrc
import structobject

uimgr = None

def get():
    return uimgr

class UIManager(object):
    def __init__(self, resource_file, top_level_name, top_level_type="frame", reuse_app=False, load_on=None):
        global uimgr
        self._event_aliases = {}
        self.resource_name = resource_file
        if not reuse_app:
            self.app = wx.App(redirect=False)
        else:
            self.app = wx.GetApp()
        self.resource = xrc.XmlResource(resource_file)
        self.top_level = getattr(self, "get_%s"%top_level_type)(top_level_name, load_on)
        self.app.TopLevelWindow = self.top_level
        self.add_event_alias("button", "clicked")
        self.add_event_alias("menu", "selected")
        self._dlg_stack = []
        self.current_dialog = None
        uimgr = self

    def get_frame(self, name, load_on=None):
        if load_on:
            self.resource.LoadFrame(load_on, getattr(self, "top_level", None), name)
            return load_on
        else:
            return self.resource.LoadFrame(getattr(self, "top_level", None), name)

    def get_dialog(self, name, load_on=None):
        if load_on:
            self.resource.LoadDialog(load_on, self.usable_parent, name)
            return load_on
        else:
            return self.resource.LoadDialog(self.usable_parent, name)
    def auto_bind(self, parent, eventsobj, only=[], alternate_bind_of=[]):
        if eventsobj is None: return
        handlers = [name for name in dir(eventsobj) if name.startswith("on_")]
        olen = len(only)
        for h in handlers:
            try:
                on, name, event = h.split("_", 2)
            except ValueError: raise ValueError("Supposed handler %s has wrong name."%h)
            if olen != 0 and name not in only: continue
            event = self._lookup_event(event)
            parent.Bind(event, getattr(eventsobj, h), id=xrc.XRCID(name))
        for a in alternate_bind_of: self._alternate_bind(parent, a, eventsobj)

    def run(self, show=True):
        if show: self.top_level.Show()
        self.app.MainLoop()

    def close(self):
        if self.usable_parent:
            self.top_level.Close()
        self.app.ExitMainLoop()

    def add_event_alias(self, wx_event, event):
        self._event_aliases[event] = wx_event

    def show_error(self, title, message):
        wx.MessageBox(message, title, parent=self.current_dialog or self.top_level, style=wx.ICON_ERROR|wx.OK)

    def get_values(self, parent, *vals):
        result = {}
        for name in vals:
            try:
                result[name] = parent.FindWindowByName(name).Value
            except AttributeError:
                result[name] = parent.FindWindowByName(name).Selection

        return structobject.Structobject(**result)
    
    def set_values(self, parent, valsobj, *vals):
        for name in vals:
            try:
                parent.FindWindowByName(name).Value = unicode(getattr(valsobj, name, ""))
            except AttributeError:
                parent.FindWindowByName(name).Selection = getattr(valsobj, name)
   
    def clear_fields(self, parent, *fields):
        for f in fields:
            parent.FindWindowByName(f).Value = ""

    def show_dialog(self, name, eventsobj=None, only=[], alternate_bind_of=[]):
        dlg = self.prepare_show_dialog(name, eventsobj, only, alternate_bind_of)
        dlg.ShowModal()

    def prepare_show_dialog(self, name, eventsobj=None, only=[], alternate_bind_of=[]):
        dlg = self.get_dialog(name)
        if self.current_dialog is not None:
            dlg.Bind(wx.EVT_CLOSE, self._unwind_stack)
        self._dlg_stack.append(dlg)
        self.current_dialog = dlg
        if eventsobj:
            self.auto_bind(self.current_dialog, eventsobj, only, alternate_bind_of)
        else: # The subclassing case
            self.auto_bind(self.current_dialog, self.current_dialog, only, alternate_bind_of)
        #Hack to make wxgtk's focus strangeness happy
        #Sets focus to the first non statictext widget of the panel which must be there, so we don't care... It could go wrong though in the future.
        for c in self.current_dialog.Children[0].Children:
            if not isinstance(c, wx.StaticText):
                c.SetFocus()
                break
        return dlg

    def prepare_xrc_dialog(self, cls, alternate_bind_of=[], parent=None, **post_init_kwargs):
        if not parent: parent = self.top_level
        inst = cls()
        if hasattr(wx, "PreDialog"):
            pre = wx.PreDialog()
            self.resource.LoadOnDialog(pre, parent, cls.xrc_name)
            inst.PostCreate(pre)
        else: # Phoenix
            self.resource.LoadDialog(inst, parent, cls.xrc_name)
        self.auto_bind(inst, inst, alternate_bind_of=alternate_bind_of)
        if hasattr(inst, "post_init"): inst.post_init(**post_init_kwargs)
        return inst
        
    def _unwind_stack(self, evt):
        try: self._dlg_stack.remove(self.current_dialog)
        except ValueError: pass
        try: self.current_dialog = self._dlg_stack.pop()
        except IndexError: self.current_dialog = None
        evt.Skip()

    def _alternate_bind(self, parent, meth, evtobj):
        on, name, event = meth.split("_", 2)
        evt = self._lookup_event(event)
        parent.FindWindowByName(name).Bind(evt, getattr(evtobj, meth))

    def _lookup_event(self, evt):
        if not hasattr(wx, "EVT_%s"%evt.upper()):
                evt = self._event_aliases[evt]
        return getattr(wx, "EVT_%s"%evt.upper())

    @property
    def usable_parent(self):
        obj = getattr(self, "top_level", None)
        if not issubclass(obj.__class__, wx.Window): return None
        return obj