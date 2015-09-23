# -- coding: UTF-8 -- 
import wx
import uimanager

class NodeProperties(wx.Dialog):
    xrc_name = "node_properties"

    def __init__(self): pass

    def post_init(self, node):
        self.node = node
        self.added_tags = []
        self.removed_tags = []
        self.FindWindowByName("tags").AppendItems(node.tags)

    def on_removetag_clicked(self, evt):
        if wx.MessageBox(_("Confirm"), _("Do you really want to remove the tag?"), style=wx.ICON_QUESTION|wx.YES_NO|wx.NO_DEFAULT, parent=self) == wx.YES:
            lst = self.FindWindowByName("tags")
            n = lst.Selection
            self.removed_tags.append(lst.GetString(n))
            lst.Delete(n)

    def on_addtag_clicked(self, evt):
        tag = wx.GetTextFromUser(_("Tag name"), _("Enter the tag name"), parent=self)
        if tag:
            self.added_tags.append(tag)
            self.FindWindowByName("tags").Append(tag)

    def on_ok_clicked(self, evt):
        for tag in self.removed_tags:
            self.node.tags.remove(tag)
        for tag in self.added_tags:
            self.node.tags.append(tag)
        if len(self.added_tags) or len(self.removed_tags):
            uimanager.get().top_level.file.modified = True
        self.Destroy() # From this place Close does not work

    def on_cancel_clicked(self, evt):
        self.Destroy()