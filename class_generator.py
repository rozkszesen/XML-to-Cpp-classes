import sys
import copy as c

from classes import *
from codegenerator import *

class Parser:
    '''used for parsing the scanned tokens and creating proper classes'''
    def __init__(self) -> None:
        self.t = Tokenizer()
        self.c = Code_Generator()
        self.tokens = []
        self.classes = []
        self.instances = []

    def do(self, file):
        ''' scan input file and extract tokens, parse tokens to generate classes and objects, generate main and header files'''
        self.tokens = self.t.scan(file)
        self.parseTokens()
        self.c.generateFiles(self.classes, self.instances)
    
    def parseTokens(self):
        tokens = c.copy(self.tokens) # copy the contents, not bind to the same memory address, so we dont modify self.tokens
        
        # check first 3 tokens if they are <, root_tag, and >
        if(tokens[0] == ("<", 0)):
            if tokens[1][1] == 1:

                if tokens[2] == (">", 0):
                    root = tokens[1][0]

                elif tokens[2] == ("/", 0) and tokens[3] == (">", 0):
                # if the xml file contains only <root/>
                    if len(self.tokens) == 4:
                        # exit parsing and generate only main.cpp file with empty main fun.
                        print("Generate empty main function in main.cpp file.")
                        return
                    else:
                        # there appeared additional elements beside <root/>
                        self.errorParse("Invalid syntax.")

                else:
                        self.errorParse("Invalid syntax.")

            else:
                self.errorParse("Unexpected token type in place of root tag.")
            
            for _ in range(3):
                tokens.pop(0)
       
        # check if the last 4 tokens are <root_tag\> (otherwise parsing the whole token list is pointless)
        if (len(tokens) >= 4 and tokens[-1] == (">", 0) and tokens[-3] == ("/", 0) and tokens[-4] == ("<", 0)):
            if(tokens[-2][0] == root):
                if (len(tokens) == 4):
                    # exit parsing and generate only main.cpp file with empty main fun.
                    print("Generate empty main function in main.cpp file.")
                    return
                else:
                    # pop root element from the token list and continue parsing
                    for _ in range(4):
                        tokens.pop()
            else:
                self.errorParse("The parent element must have a matching closing tag.")
        else:
            self.errorParse("The parent element must have a matching closing tag.")

        '''
        print("\n\ncurrent tokens:")    
        for token in tokens:
            print(token) 
        print("\n")
        '''

        # CONTINUE PARSING 

        while len(tokens) != 0:
            # expect an element
            if tokens[0] == ("<", 0):
                tokens.pop(0) # pop the "<" operator

                if(tokens[0][1] == 1 and tokens[1][1] == 2):
                # detected element has tag and attribute(s)
                    self.readElement(tokens)

                elif(tokens[0][1] == 1 and tokens[0] == (">", 0)):
                # detected element has tag and no attributes => it's a container
                    self.readContainer(tokens)

                else:
                    self.errorParse("Unexpected token.")

            else:
                self.errorParse("Invalid syntax. Opening tag missing.")
                

    def readElement(self, tokens):
        ''' reads element name and attributes and creates classes and instances accordingly '''

        # read element name
        name = tokens.pop(0)[0]
        tempClass = Cpp_class()
        tempObject = Cpp_object(name)
        # do not append self.instances and self.classes yet.
        
        if(tokens[0][1] == 2):
        # attribute detected
            while tokens[0] != ("/", 0) and tokens[0] != (">", 0):
                
                if(tempClass.add_attribute(tokens[0][0])):
                    self.errorParse("Attribute name repeated in the same element.")

                if(tokens.pop(1) == ("=", 0) and tokens[1][1] == 3):
                # if attribute is followed by "=" operator and stringvalue, read the attr name and value and pop elements from the list
                    tempObject.attributes[tokens[0][0]] = tokens[1][0]
                    tokens.pop(0)
                    tokens.pop(0)

                else:
                    self.errorParse("Invalid syntax in attribute declaration.")              

            
            if tokens[0] == (">", 0):
                # Missing closing tag
                self.errorParse("Missing closing tag '/>'.")
            elif tokens[0] == ("/", 0) and tokens[1] == (">", 0):
                # add created class to class list and update base class id of the created object. Add the object to the list of instances
                tempObject.baseClassId = self.getId(self.addClass(tempClass))
                self.addInstance(tempObject)
                tokens.pop(0)
                tokens.pop(0)
            
            else:
                self.errorParse("Missing operator.")
    

    def addClass(self, newClass):
        '''returns "pointer" to the added class or to the existing one in the list of classes, that is equal to the passed class'''

        if(newClass not in self.classes):
            self.classes.append(newClass)
            return newClass
        else:
            # class already exists in the set of classes, return "pointer" to the found class
            return self.getSameClass(newClass)

    def getId(self, cl):
        '''returns the id (number in the class list) of the given class'''
        for i in range(len(self.classes)):
            if(cl == self.classes[i]):
                return i
        
        self.error("Couldn't find given class in the list of classes.")
    
    def getSameClass(self, other):
        '''returns "pointer" to the class from list of classes that is equal to the class passed as a parameter'''
        for c in self.classes:
            if c == other:
                return c
        
        return None

    def addInstance(self, newObject):
        '''adds object to the list of instances if object of such name doesn't exists on the list yet'''

        if newObject in self.instances:
            self.error("Trying to declare an object with name that is already taken.")

        else:   
            self.instances.append(newObject)

    def errorParse(self, message = ''):
        sys.exit("Error during parsing. " + message)
    
    def error(self, message =''):
        sys.exit("Error. " + message)


class Tokenizer:
    # used for reading the xml file and producing tokens
    def __init__(self) -> None:
        self.tokens = []    # an array of tuples holding the tokens with assigned types
                            # token types: 0-OPERATOR, 1-TAG, 2-ATTRIBUTE, 3-STRINGVALUE
        self.forbiddenAscii = self.generateForbiddenAscii()
        self.operators = {'<', '>', '/', '=', '"', ' '}
        self.linesScanned = 0
        
    def scan(self, filename):
        
        file = open(filename, "r", encoding='ascii') 
        '''
        try:
            c = file.read()
        except Exception:
            print("File contains characters that can't be decoded with ascii codec.")
        '''
        
        c = file.read(1)

        is_quote = 0
        is_element = 0
        has_tag = 0
        is_attribute = 0
        equal_sign = 0
        
        while(c != ''):
            self.linesScanned += 1

            while(c != '\n' and c != ''):
                if(c in self.operators):
                    # if  < then we're at the beginning of an element
                    if (c == "<" and is_element == 0):
                        is_element = 1
                        self.tokens.append((c, 0))
                    
                    # if > then we're closing an element and we no longer care about the existence of tag
                    # what is also checked: if we already started an element and if it has a tag
                    elif(c == ">" and is_element == 1 and has_tag == 1):
                        is_element = 0
                        has_tag = 0
                        self.tokens.append((c, 0))

                    elif(c == ' '):
                        pass

                    #if detected operator is a quote: read a string of any characters untill next quote:
                    elif(is_element == 1 and has_tag == 1 and is_attribute == 1 and equal_sign == 1):
                        if(c == '"' ):
                            if(is_quote == 0 and equal_sign == 1):
                                # if it's a starting quote and attribute name was detected
                                c = file.read(1)
                                string = self.readString(file)
                                self.tokens.append((string, 3))
                                is_quote = 1

                            elif(is_quote == 1):
                                is_quote = 0
                                is_attribute = 0
                                equal_sign = 0
                            
                        else:
                            self.errorChar(self.linesScanned, "Unexpected operator.")
                    
                    elif(is_attribute == 1 and equal_sign == 0):
                        if(c == "="):
                            # check for equal sign after attribute name
                            self.tokens.append((c, 0))
                            equal_sign = 1
                        else:
                            self.errorChar(self.linesScanned, "'=' missing in attribute declaration.")

                    elif(c == "/"):
                        self.tokens.append((c, 0))
                    
                    else:
                        # unexpected operator detected
                        self.errorChar(self.linesScanned, "Unexpected operator.")
                
                elif((ord(c) in range(65,91) or ord(c) in range(97,123)) and is_element == 1):
                    if(has_tag == 0):
                        # tag detected
                        has_tag = 1
                        tag = self.readTag(file)
                        self.tokens.append((tag, 1))
                    elif(has_tag == 1 and is_attribute == 0):
                        # attribute detected
                        is_attribute = 1
                        attribute = self.readTag(file)
                        self.tokens.append((attribute, 2))

                else:
                    # unexpected character
                    self.errorChar(self.linesScanned, "Unexpected character " + c + ".")

                # continue scanning
                c = file.read(1)

            c = file.read(1)
        
        '''
        for token in self.tokens:
            print(token)
        '''

        if len(self.tokens) == 0:
            self.errorChar(self.linesScanned)

        file.close()

        return self.tokens
            
    def readTag(self, file):
        # read string of characters allowed for a Tag untill meets an operator or a forbidden character
        file.seek(file.tell()-1) # move the pointer one char back to read the first character
        tag = ''

        c = file.read(1)
        while(c not in self.operators):
            if(ord(c) not in self.forbiddenAscii):
                tag += c
            else:
                self.errorChar(self.linesScanned, "Forbidden character " + str(c) + ".")
            c = file.read(1)

        file.seek(file.tell()-1) # move the pointer one char back
        
        return tag

    def readString(self, file):
        # read string of characters allowed for a Tag untill meets an operator or a forbidden character
        file.seek(file.tell()-1) # move the pointer one char back
        string = ''

        c = file.read(1)
        while(c != '"' and c != '\n'):
            string += c
            c = file.read(1)

        file.seek(file.tell()-1) # move the pointer one char back
        
        return string

    def generateForbiddenAscii(self):
        #returns a set of forbidden ascii characters in range 32-123
        ascii=set()

        for n in range(33,48):
            #!"#$%&'()*+,-./
            ascii.add(n)

        for n in range(58,65):
            #:;<=>?@
            ascii.add(n)
        
        for n in range(91,95):
            #[\]^
            ascii.add(n)

        # underscore (ascii = 95) is allowed

        ascii.add(96) #'

        for n in range(123,127):
            #{|}~
            ascii.add(n)

        #127+ are extended ascii characters
        return ascii

    def errorChar(self, line_number, message = ''):
        print("Error during scanning, in line " + str(line_number) + ". " + message)
        sys.exit()
        

if __name__ == '__main__':
    p = Parser()

    if len(sys.argv) != 2:
        print(len(sys.argv))
        sys.exit("Please provide the name of the input XML file.")
        
    filename = sys.argv[1]

    p.do(filename)
    