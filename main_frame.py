# -- coding: UTF-8 --
import sys
import wx, pdb
import wx.xrc as xrc
import PyOrgMode
import uimanager
import node_properties
import orgutils
import sodium_utils

wildcard = _("ORG files (*.org)|*.org")

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__() # It works, somehow there...
        self.file = None
        self.prev_node = None

    def on_tree_tree_sel_changed(self, evt):
        item = evt.Item
        txt = self.FindWindowByName("text")
        if self.prev_node and txt.IsModified():
            orgutils.set_org_text(self.prev_node, txt.Value)
            self.file.modified = True
        node = self.FindWindowByName("tree").GetItemData(item)
        lines = [i for i in node.content if isinstance(i, str)] # It ends with a new line anyway, see the modification in PyOrgMode.py.
        text = "".join(lines)
        txt.Value = text
        self.prev_node = node
        rid = xrc.XRCID("remove")
        # Removing the only node of the 1st level would break everything else
        if node.level == 1 and len(node.parent.content) == 1:
            self.MenuBar.Enable(rid, False)
        else:
            self.MenuBar.Enable(rid, True)
        # And some movement operations would not be possible as well in some cases
        self.MenuBar.Enable(xrc.XRCID("left"), node.level != 1)
        self.MenuBar.Enable(xrc.XRCID("right"), len(node.parent.content) != 1)
        self.MenuBar.Enable(xrc.XRCID("up"), node.parent.content.index(node) != 0)
        self.MenuBar.Enable(xrc.XRCID("down"), node.parent.content[-1] != node)
        # Time recording if requested
        if self.file.track_times:
            orgutils.set_node_property(node, "accessed", orgutils.current_time())

    
    def on_open_selected(self, evt):
        path = wx.FileSelector(_("Select file"), wildcard=wildcard, flags=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST, parent=self)
        if path:
            self.open_file(path)
    
    def on_saveas_selected(self, evt, set_name=False):
        path = wx.FileSelector(_("Select file"), wildcard=wildcard, flags=wx.FD_SAVE, parent=self)
        if path:
            self.update_current_node_text()
            if self.file.track_tree_state: # Update the selected item before saving if needed
                node = self.tree.GetItemData(self.tree.Selection)
                self.file.selected_item = orgutils.get_node_path(node)
            orgutils.save_file(self.file, path)
            if set_name:
                self.file_name = path
    
    def on_save_selected(self, evt):
        self.update_current_node_text()
        if self.file.modified:
            if self.file_name:
                if self.file.track_tree_state: # Update the selected item before saving if needed
                    node = self.tree.GetItemData(self.tree.Selection)
                    self.file.selected_item = orgutils.get_node_path(node)
                orgutils.save_file(self.file, self.file_name)
                self.file.modified = False
            else:
                self.on_saveas_selected(evt, True)
    
    def do_add_same_level(self, index_fn):
        node, heading = self.create_node()
        if node:
            tree = self.FindWindowByName("tree")
            si = tree.Selection
            selected = tree.GetItemData(si)
            this_idx = index_fn(selected.parent.content.index(selected))
            node.parent = selected.parent
            node.level = selected.level
            selected.parent.content.insert(this_idx, node)
            nodes = [n for n in selected.parent.content if isinstance(n, PyOrgMode.OrgNode.Element)]
            tree_idx = index_fn(nodes.index(selected))
            new = tree.InsertItem(tree.GetItemParent(si), tree_idx, heading)
            tree.SetItemData(new, node)
            self.populate_branch(node, existing_item=new)
            tree.SetFocusedItem(new)
            tree.ToggleItemSelection(new)
            self.FindWindowByName("text").Clear()
            self.file.modified = True
            self.MenuBar.Enable(xrc.XRCID("remove"), True) # Definitely something can be removed
    
    def on_addbefore_selected(self, evt): self.do_add_same_level(lambda i: i)
    def on_addafter_selected(self, evt): self.do_add_same_level(lambda i: i + 1)
    
    def on_addchild_selected(self, evt):
        node, heading = self.create_node()
        if node:
            tree = self.FindWindowByName("tree")
            si = tree.Selection
            selected = tree.GetItemData(si)
            node.parent = selected
            node.level = selected.level + 1
            selected.content.append(node)
            new = tree.AppendItem(si, heading)
            tree.SetItemData(new, node)
            self.populate_branch(node, existing_item=new)
            tree.SetFocusedItem(new)
            tree.ToggleItemSelection(new)
            self.FindWindowByName("text").Clear()
            self.file.modified = True

    def on_rename_selected(self, evt):
        tree = self.FindWindowByName("tree")
        si = tree.Selection
        new_name = wx.GetTextFromUser(_("Enter a title for the node"), _("Node title"), default_value=tree.GetItemText(si), parent=self)
        if new_name:
            tree.SetItemText(si, new_name)
            tree.GetItemData(si).heading = new_name
            self.file.modified = True
    
    def on_remove_selected(self, evt):
        if wx.MessageBox(_("Do you really want to remove the node?"), _("Confirm"), style=wx.YES_NO|wx.ICON_QUESTION|wx.NO_DEFAULT, parent=self) == wx.YES:
            tree = self.FindWindowByName("tree")
            si = tree.Selection
            node = tree.GetItemData(si)
            tree.Delete(si)
            node.parent.content.remove(node)
            self.file.modified = True
            self.MenuBar.Enable(xrc.XRCID("remove"), tree.Count > 1)
    
    def do_same_level_move(self, index_fn):
        tree = self.FindWindowByName("tree")
        si = tree.Selection
        pi = tree.GetItemParent(si)
        node = tree.GetItemData(si)
        idx = node.parent.content.index(node)
        el = node.parent.content
        el[idx], el[index_fn(idx)] = el[index_fn(idx)], el[idx]
        tree.Delete(si)
        nodes = [n for n in node.parent.content if isinstance(n, PyOrgMode.OrgNode.Element)]
        tree_idx = index_fn(nodes.index(node))
        new = tree.InsertItem(pi, tree_idx, node.heading.decode("UTF-8"))
        tree.SetItemData(new, node)
        self.populate_branch(node, existing_item=new)
        tree.SetFocusedItem(new)
        tree.ToggleItemSelection(new)
        self.file.modified = True
    
    def on_up_selected(self, evt): self.do_same_level_move(lambda i: i - 1)
    def on_down_selected(self, evt): self.do_same_level_move(lambda i: i + 1)
    
    def on_right_selected(self, evt):
        tree = self.FindWindowByName("tree")
        si = tree.Selection
        prev = tree.GetPrevSibling(si)
        node = tree.GetItemData(si)
        idx = node.parent.content.index(node)
        node.parent.content.remove(node)
        node.parent.content[idx - 1].content.append(node)
        node.parent = node.parent.content[idx - 1]
        node.level += 1
        tree.Delete(si)
        new = tree.AppendItem(prev, node.heading.decode("UTF-8"))
        tree.SetItemData(new, node)
        self.populate_branch(node, existing_item=new)
        tree.SetFocusedItem(new)
        tree.ToggleItemSelection(new)
        self.file.modified = True
    
    def on_left_selected(self, evt):
        tree = self.FindWindowByName("tree")
        si = tree.Selection
        node = tree.GetItemData(si)
        parent_idx = node.parent.parent.content.index(node.parent)
        node.parent.content.remove(node)
        node.parent.parent.content.insert(parent_idx + 1, node)
        node.parent = node.parent.parent
        node.level -= 1
        pi = tree.GetItemParent(tree.GetItemParent(si))
        tree.Delete(si)
        nodes = [n for n in node.parent.parent.content if isinstance(n, PyOrgMode.OrgNode.Element)]
        parent_tree_idx = nodes.index(node.parent)
        new = tree.InsertItem(pi, parent_tree_idx + 1, node.heading.decode("UTF-8"))
        tree.SetItemData(new, node)
        tree.SetFocusedItem(new)
        self.populate_branch(node, existing_item=new)
        tree.ToggleItemSelection(new)
        self.file.modified = True
    
    def on_new_selected(self, evt):
        if self.prompt_save_if_needed():
            self.create_new_file()
    
    def on_quit_selected(self, evt):
        if isinstance(evt, wx.CommandEvent): # Clicked the menu item, we must actually exit the app or, better said, initiate the sequence
            self.Close()
        else: # Window is closing for some reason (item click, system shutdown, the x icon clicked etc.)
            if not self.prompt_save_if_needed(): # If we *are not* allowed to continue and should cancel the operation
                if evt.CanVeto(): evt.Veto() # No reason for trying to veto something that we actually can't
            else: # Let the toolkit continue the event handling normally, leading ultimately to the app exit
                # calling evt.Skip only sometimes resulted in an access violation. Maybe, this will fare better.
                self.Destroy()
                
    
    # Note for all those below, calling update_current_note_text is pointless, they'll be called more appropriately when leaving the current node or requesting a save.
    def on_undo_selected(self, evt):
        self.FindWindowByName("text").Undo()
    
    def on_cut_selected(self, evt):
        self.FindWindowByName("text").Cut()
    
    def on_copy_selected(self, evt):
        self.FindWindowByName("text").Copy()
    
    def on_paste_selected(self, evt):
        self.FindWindowByName("text").Paste()
    
    def on_delete_selected(self, evt):
        self.FindWindowByName("text").Delete()

    def on_properties_selected(self, evt):
        dlg = uimanager.get().prepare_xrc_dialog(node_properties.NodeProperties, node=self.tree.GetItemData(self.tree.Selection))
        dlg.AffirmativeId = xrc.XRCID("ok")
        dlg.EscapeId = xrc.XRCID("cancel")
        dlg.ShowModal()

    def on_encrypt_selected(self, evt):
        pass1 = wx.GetPasswordFromUser(_("Enter the encryption password"), _("Password required"))
        if not pass1: # Either unencrypt or cancel
            if self.file.password:
                if wx.MessageBox(_("Do you really want to decrypt the file?"), _("Question"), style=wx.YES_NO|wx.ICON_QUESTION) == wx.YES:
                    self.file.password = None
                    self.file.modified = True
                return # Ignoring the question, it's end of the querying for now.
            else:
                return
        pass2 = wx.GetPasswordFromUser(_("Enter the same password again"), _("Password required"))
        if not pass2: return
        if pass1 != pass2:
            wx.MessageBox(_("Provided passwords do not match, try again."), _("Error"), icon=wx.ICON_ERROR)
        else:
            self.file.password = pass1
            self.file.modified = True
    def on_tree_tree_item_activated(self, evt): self.on_properties_selected(evt)

    def on_tree_tree_item_menu(self, evt):
        mnu = uimanager.get().resource.LoadMenu("node_menu")
        self.tree.PopupMenu(mnu, evt.Point)

    def on_tree_tree_item_expanded(self, evt):
        if self.file.track_tree_state:
            orgutils.set_node_property(self.tree.GetItemData(evt.Item), "expanded", "True")

    def on_tree_tree_item_collapsed(self, evt):
        if self.file.track_tree_state:
            orgutils.delete_node_property(self.tree.GetItemData(evt.Item), "expanded")

    # Helpers

    def populate_branch(self, node, parent=None, existing_item=None):
        tree = self.tree
        if not existing_item:
            selfitem = tree.AppendItem(parent, (node.heading or _("<Unnamed node>")))
            tree.SetItemData(selfitem, node)
        else:
            selfitem = existing_item
        for c in node.content:
            if isinstance(c, PyOrgMode.OrgNode.Element): self.populate_branch(c, selfitem)
        if self.file.track_tree_state:
            if orgutils.get_node_property(node, "expanded"):
                tree.Expand(selfitem)
    
    def populate_tree(self, org_data):
        item = self.tree.AddRoot("Never to be seen")
        for el in org_data.root.content: # Nothing else than elements, so creating the unnamed root is pointless (the TreeView api should not distinguish between root and other items, then it would be just the question of hiding the root)
            if isinstance(el, PyOrgMode.OrgNode.Element):
                self.populate_branch(el, item)
            else:
                print("Found item of type %s in root level: %r"%(type(el), el))
            self.MenuBar.Enable(xrc.XRCID("remove"), self.tree.Count > 1)
    
    def open_file(self, fname):
        self.file = PyOrgMode.OrgDataStructure()
        self.file_name = fname
        self.file.load_from_file(fname)
        self.file.modified = False
        self.tree.DeleteAllItems()
        if not isinstance(self.file.root.content[0], PyOrgMode.OrgNode.Element): # Assume they're flags
            self.file = orgutils.set_file_flags_on(self.file, self.file.root.content[0])
            del self.file.root.content[0] # We don't need them there anymore
        else:
            self.file.track_times = False
            self.file.track_tree_state = False
            self.file.selected_item = None
            self.file.password = None # Note that something like .net's SecureString would be nice, but there is no cross platform way, or atleast none i am aware of.
        if self.file.password: # Encrypted
            has_password = False
            while not has_password:
                password = wx.GetPasswordFromUser(_("Enter the password used to encrypt the file"), _("Password required"))
                if not password: return
                try:
                    data = sodium_utils.decrypt(self.file.root.content[0], password)
                    self.file.password = password
                    self.file.root.content = []
                    self.file.load_from_string(data)
                    has_password = True
                except ValueError:
                    wx.MessageBox(_("The provided password is invalid."), _("Error"), style=wx.ICON_ERROR)
        self.populate_tree(self.file)
        if self.file.selected_item:
            last = self.get_item_by_path(self.file.selected_item)
            self.tree.SetFocusedItem(last)
            self.tree.ToggleItemSelection(last)
        else:
            item = self.tree.FirstVisibleItem
            self.tree.SetFocusedItem(item)
            self.tree.ToggleItemSelection(item)
    
    def create_new_file(self):
        self.tree.DeleteAllItems()
        self.file = PyOrgMode.OrgDataStructure()
        self.file_name = None
        self.file.load_from_string("* " + _("First node"))
        self.file.modified = False
        self.file.track_times = False
        self.file.track_tree_state = False
        self.file.selected_item = None
        self.file.password = None
        self.populate_tree(self.file)
        
    def update_current_node_text(self):
        tree = self.tree
        txt = self.FindWindowByName("text")
        if txt.IsModified(): # Persist current changes
            orgutils.set_org_text(tree.GetItemData(tree.Selection), txt.Value)
            self.file.modified = True    
            txt.SetModified(False)
            if self.file.track_times:
                orgutils.set_node_property(tree.GetItemData(tree.Selection), "modified", orgutils.current_time())

    def create_node(self):		
        name = wx.GetTextFromUser(_("Enter a name for the new node"), _("Node title"), parent=self)
        if name:
            node = PyOrgMode.OrgNode.Element()
            node.heading = name
            if self.file.track_times:
                orgutils.set_node_property(node, "created", orgutils.current_time())
            return node, name
        return None, None # User cancelled or no name given
    
    def prompt_save_if_needed(self):
        self.update_current_node_text() # Also updates the modified flag if needed, which is quite desirable
        if self.file.modified:
            dlg = wx.MessageDialog(self, _("Save the changes in this file?"), _("Question"), style=wx.YES_NO|wx.CANCEL)
            dlg.SetYesNoCancelLabels(_("Save"), _("Don't save"), _("Cancel"))
            resp = dlg.ShowModal()
            if resp == wx.ID_YES:
                self.on_save_selected(None)
            return resp != wx.ID_CANCEL
        else: # Nothing changed
            return True # Ok to continue with whatever you're doing

    @property
    def tree(self):
        return self.FindWindowByName("tree")

    def get_nth_child(self, item, n):
        tree = self.tree
        i, cookie = tree.GetFirstChild(item)
        for i in range(int(n)):
            i, cookie = tree.GetNextChild(item, cookie)
        return i

    def get_item_by_path(self, path):
        elems = path.split("/")
        ctx = self.tree.RootItem
        for el in elems:
            ctx = self.get_nth_child(ctx, el)
        return ctx