import time
import PyOrgMode

def set_org_text(node, text):
    text_lst = [item + "\n" for item in text.split("\n")]
    others = [el for el in node.content if not isinstance(el, str)]
    text_lst.extend(others)
    node.content = text_lst

def get_node_property(node, property, default=None):
    drawer = [e for e in node.content if isinstance(e, PyOrgMode.OrgDrawer.Element) and e.name == "PROPERTIES"]
    if len(drawer) != 1: return default # Not found or multiple property areas found
    prop = [p for p in drawer[0].content if p.name == property]
    if len(prop) != 1: return default # No such property or multiple definition
    return prop[0].value

def set_node_property(node, property, value):
    drawer = [e for e in node.content if isinstance(e, PyOrgMode.OrgDrawer.Element) and e.name == "PROPERTIES"]
    if not drawer: # No properties existed there before
        drawer = PyOrgMode.OrgDrawer.Element("PROPERTIES")
        node.content.insert(0, drawer)
    else:
        drawer = drawer[0]
    prop = [p for p in drawer.content if p.name == property]
    if not prop: # No such property - add
        prop = PyOrgMode.OrgDrawer.Property(property)
        drawer.content.append(prop)
    else: # Update
        prop = prop[0]
    prop.value = value

def delete_node_property(node, property):
        drawer = [e for e in node.content if isinstance(e, PyOrgMode.OrgDrawer.Element) and e.name == "PROPERTIES"]
        if drawer:
            drawer = drawer[0]
            prop = [p for p in drawer.content if p.name == property]
            if prop:
                prop = prop[0]
                drawer.content.remove(prop)
                if len(drawer.content) == 0: # No properties left
                    node.content.remove(drawer)

def current_time():
    t = time.localtime()
    return time.strftime("%Y-%m-%d %H:%M:%S", t)

def get_node_path(node):
    path = []
    while node.parent:
        nodes = [e for e in node.parent.content if isinstance(e, PyOrgMode.OrgNode.Element)]
        path.insert(0, str(nodes.index(node)))
        node = node.parent
    return "/".join(path)

def set_file_flags_on(file, flags):
    splitted = [f.strip() for f in flags.split(" ")]
    for flag in splitted:
        if flag == "track_times":
            file.track_times = True
        elif flag == "track_tree_state":
            file.track_tree_state = True
        elif flag.startswith("selected_item="):
            file.selected_item = flag.split("=")[1]
    elif flag == "org_encrypted":
        file.password = "something" # We'll ask anyway
    # Now the defaults
    if not hasattr(file, "track_times"): file.track_times = False
    if not hasattr(file, "track_tree_state"): file.track_tree_state = False
    if not hasattr(file, "selected_item"): file.selected_item = None
    if not hasattr(file, "password"): file.password = None
    return file

def save_file(file, path):
    flags = []
    if file.track_times:
        flags.append("track_times")
    if file.track_tree_state:
        flags.append("track_tree_state")
    if file.selected_item:
        flags.append("selected_item=%s"%file.selected_item)
    if flags:
        flags.insert(0, "#FLAGS:")
        file.root.content.insert(0, " ".join(flags) + "\n")
    file.save_to_file(path)
    if flags:
        del file.root.content[0] # We don't need them there
    file.modified = False