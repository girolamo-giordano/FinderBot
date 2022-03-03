from botbuilder.core import StoreItem
from enum import Enum

class EnumUser(Enum):
    NAME=1
    DONE=2


class UserProfile(StoreItem):
    def __init__(self, name: str, contents: list):
        super(UserProfile, self).__init__()
        self.name = name
        self.contents = contents
    
    def setcontents(self,contents):
        if len(self.contents) > 3:
            if contents not in self.contents:
                self.contents.pop(0)
                self.contents.append(contents)
            else:
                self.contents.remove(contents)
                self.contents.append(contents)
        else:
            if contents not in self.contents:
                self.contents.append(contents)
            else:
                self.contents.remove(contents)
                self.contents.append(contents)
        #self.contents=f"La tua ultima ricerca è stata ricercare attrazioni che si trovano a {contents}"

    