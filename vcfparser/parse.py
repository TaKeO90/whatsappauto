from typing import List, Dict,NamedTuple
import os


class Contact(NamedTuple):
    FN:str
    N:str
    TEL:str

class ParseVcf:
    def __init__(self,filename:str):
        self.filename = filename

    def Parse(self):
        try : 
            assert self.filename.endswith(".vcf")
            _,ext = os.path.split(self.filename)
            ext = ext.split(".")[1]
        except AssertionError as a :
            raise AssertionError(f"want (.vcf) got ({ext})")

        try : 
            with open(self.filename,"r") as vfile :
                buff = vfile.readlines()
                self.elements = [x for x in buff if x.startswith("FN") or x.startswith("N") or x.startswith("TEL")]
        except FileNotFoundError :
            raise FileNotFoundError("File Not Found")

    def GetContacts(self) -> List[Contact]:
        preAdd, contacts = [] , []
        m = dict.fromkeys(list(Contact.__dict__["_fields"]),None)
        for e in self.elements:
            if e.startswith("FN"):
                if (fn := e.split(":")[-1].strip("\n")) != "":
                    m["FN"] = fn
                    preAdd.append(m["FN"])

            elif e.startswith("N"):
                if (n := e.split(";")[1]) != "" :
                    m["N"] = n
                    preAdd.append(m["N"])

            elif e.startswith("TEL"):
                if (tel := e.split(":")[-1].strip("\n")) != "":
                    m["TEL"] = tel
                    preAdd.append(m["TEL"])

            if len(preAdd) == 3:
                contacts.append(Contact(preAdd[0],preAdd[1],preAdd[2]))
                preAdd = []
        return contacts
