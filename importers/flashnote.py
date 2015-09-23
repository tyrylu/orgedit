"""A Flashnote importer."""
import sqlite3

def import_level(db, dest, parent, number):
    res = db.execute("SELECT * FROM notes3 WHERE pid = ? ORDER BY folderpos", [parent])
    for row in res:
        dest.write("%s %s\n"%("*" * number, row["name"].encode("UTF-8")))
        dest.write(":PROPERTIES:\n:created: %s\n:modified: %s\n:END:\n"%(row["created"], row["modified"]))
        if row["note"]:
            dest.write("%s\n"%row["note"].encode("UTF-8"))
        import_level(db, dest, row["id"], number + 1)


fname = raw_input("Flashnote database: ")
db = sqlite3.connect(fname)
db.row_factory = sqlite3.Row
dest = fname.replace(".db", ".org")
dest = open(dest, "w")
import_level(db, dest, 0, 1)
dest.close()