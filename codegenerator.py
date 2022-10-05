class Code_Generator:
    '''used for generating the code from provided lists of classes and instances'''
    def __init__(self):
        self.classes = []
        self.instances = []

    def generateFiles(self, classes, instances):
        self.classes = classes
        self.instances = instances

        if len(self.classes) == 0:
            self.generateEmptyMain()
            return
            
        self.generateHeaders()
        self.generateMain()

        
    def generateHeaders(self):
        for i in range(len(self.classes)):
            className = "Class"+ str(i+1)
            f = open(className + ".h", 'w', encoding='utf-8')

            f.write("#include <string>\n" +
                    "\n" +
                    "class " + className + " {\n" +
                    "\tprivate:\n")

            for attr in self.classes[i].attributes:
                f.write("\t\tstd::string " + str(attr) + ";\n")
            
            # default constructor and constr. with parameters
            f.write("\n" +
                    "\tpublic:\n" +
                    "\t\t" + className + "() { };\n" +
                    "\t\t" + className + "(")

            # constructor parameters
            for attr in self.classes[i].attributes:

                f.write("std::string " + str(attr))

                if(attr != self.classes[i].attributes[-1]):
                    # add only if it's not the last attribute
                    f.write(", ")
            
            # constructor body
            f.write(") {\n")
            for attr in self.classes[i].attributes:
                f.write("\t\t\tthis->" + str(attr) + " = " + str(attr) + ";\n")
            f.write("\t\t}\n\n")

            # getters and setters
            for attr in self.classes[i].attributes:
                f.write("\t\tstd::string get" + str(attr).capitalize() + "() {\n" +
                        "\t\t\treturn " + str(attr) + ";\n"+
                        "\t\t}\n"
                        "\t\tvoid set" + str(attr).capitalize() + "(" + "std::string " + str(attr) + ") {\n" +
                        "\t\t\tthis->" + str(attr) + " = " + str(attr) + ";\n" +
                        "\t\t}\n")

            f.write("};")

            f.close()

        print("Header file(s) created succesfully.")

    def generateMain(self):
        f = open("main.cpp", 'w', encoding='utf-8')
        
        f.write("#include <string>\n")
        
        #add all headers
        for i in range(len(self.classes)):
            f.write("#include <Class" + str(i+1) + ".h>\n")
        
        f.write("\nint main() {\n")
        
        # write declarations of instances
        for instance in self.instances:
            f.write("\tClass" + str(instance.baseClassId + 1) + " " + instance.name + "(")
            for value in instance.attributes.values():
                f.write('"' + value + '", ')
            f.seek(f.tell()-1)
            f.write('')
            f.seek(f.tell()-1)
            f.write(');\n')

        f.write("};")

        f.close()
        print("Main file created succesfully.")

    def generateEmptyMain(self):
        f = open("main.cpp", 'w', encoding='utf-8')

        f.write("int main() {\n\n}")
        
        f.close()
        print("Main file created succesfully.")