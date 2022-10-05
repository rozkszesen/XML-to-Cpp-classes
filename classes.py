import sys
import copy as c

class Cpp_class:
    def __init__(self, name = '') -> None:
        self.attributes = []
        self.pointers = []

    def __eq__(self, other) -> bool:
        if len(other.attributes) != len(self.attributes):
            return False

        for attr in other.attributes:
            if attr not in self.attributes:
                return False

        return True
        
    def add_attribute(self, attrName):
        # return 0 if added succesfully, return 1 if attribute already exists
        if(str(attrName) not in self.attributes):
            self.attributes.append(attrName)
            return 0
        
        else:
            return 1
    
    def add_pointer(self, name):
        if name not in self.pointers:
            pass
        else:
            # pointer already exists.
            # ( we don't want to override pointers/attributes)
            pass
    
    

class Cpp_object:
    def __init__(self, name = '') -> None:
        self.baseClassId = None
        self.name = name
        self.attributes = {} # dictionary key: value (attribute: stringvalue)
        self.pointers = {}

    def __eq__(self, other) -> bool:
        if(other.name == self.name):
            return True
        else:
            return False
