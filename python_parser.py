import sys
from entrydata import CodeEntry, CodeType
import json
import ast

# https://stackoverflow.com/questions/34570992/getting-parent-of-ast-node-in-python
class Parentage(ast.NodeTransformer):
    # current parent (module)
    parent = None

    def visit(self, node):
        # set parent attribute for this node
        node.parent = self.parent
        # This node becomes the new parent
        self.parent = node
        # Do any work required by super class 
        node = super().visit(node)
        # If we have a valid node (ie. node not being removed)
        if isinstance(node, ast.AST):
            # update the parent, since this may have been transformed 
            # to a different node by super
            self.parent = node.parent
        return node


class PythonASTParser():
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.result_list: list[CodeEntry] = []
        with open(self.filename, "r") as f:
            self.source = f.read()
            self.code = self.source.splitlines()
            try:
                tree = ast.parse(source=self.source)
            except SyntaxError:
                print(f"###### Invalid Syntax {filename}")
                return
            self.tree = Parentage().visit(tree)
            self.parse()
    
    def parse(self):
        maincodes = CodeEntry(CodeType.FUNCTION, self.filename, "")
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                bases = []
                for n in node.bases:
                    if isinstance(n, ast.Attribute):
                        base =f"{n.value.id}.{n.attr}"
                    else:
                        base = n.id
                    bases.append(base)
                ce = CodeEntry.load_class(self.filename, node.name, bases)
                ce.add_codeline(self.code[node.lineno-1])
                for n in node.body:
                    if not isinstance(n, (ast.ClassDef, ast.FunctionDef)):
                        tcode = self.code[n.lineno-1:n.end_lineno]
                        for line in tcode:
                            text = line[node.col_offset:]
                            ce.add_codeline(text)
                self.result_list.append(ce)

            elif isinstance(node, ast.FunctionDef):
                text = self.code[node.lineno-1]
                if not ":" in text:
                    texts = self.code[node.lineno-1:node.end_lineno]
                    text = " ".join(texts)
                _, arg, ret = self.python_func_parse(text)
                arg = [x for x in arg if x != ""]
                if isinstance(node.parent, ast.ClassDef):
                    name = f"{node.parent.name}.{node.name}"
                    # print(name)
                    ce = CodeEntry.load_function(self.filename, name, arg, ret)
                else:
                    # print(node.name)
                    ce = CodeEntry.load_function(self.filename, node.name, arg, ret)
                decorator = []
                for n in node.decorator_list:
                    tcode = self.code[n.lineno-1].strip()
                    decorator.append(tcode)
                ce.set_decorator(decorator)
                tcode = self.code[node.lineno-1:node.end_lineno]
                for line in tcode:
                    text = line[node.col_offset:]
                    ce.add_codeline(text)
                self.result_list.append(ce)
            else:
                if not isinstance(node, (ast.ClassDef, ast.FunctionDef)) and isinstance(node.parent, (ast.Module)):
                    if hasattr(node, "lineno"):
                        tcode = self.code[node.lineno-1:node.end_lineno]
                        for line in tcode:
                            text = line[node.col_offset:]
                            maincodes.add_codeline(text)
        self.result_list.append(maincodes)

    def args_parser(self, node: ast.arguments):
        print(ast.dump(node))
        if node.args:
            for a in node.args:
                print(a)
                print(a.arg)
                if not a.annotation is None:
                    print(a.annotation.id)
        if node.vararg:
            for a in node.vararg:
                print(a)
        if node.kwonlyargs and node.kw_defaults:
            for a in zip(node.kwonlyargs, node.kw_defaults):
                print(a)
        if node.kwarg:
            for a in node.kwarg:
                print(a)

    def python_func_parse(self, line):
        text = line.strip().replace("def ", "")
        stext = text.split("(", 1)
        name = stext.pop(0)
        stext2 = stext[0].rsplit(")", 1)
        arg = [x.strip() for x in stext2.pop(0).split(',')]
        if stext2[0].strip() == ":":
            ret = "unknown"
        else:
            ttext = stext2[0].strip().replace("->","").strip()
            ret = ttext.split(":", 1)[0]
        return name, arg, ret
        

    def list(self):
        tlist = []
        if len(self.result_list) >= 1:
            for ce in self.result_list:
                tlist.append(ce.json())
        return tlist

    def jsonstr(self):
        tlist = []
        if len(self.result_list) >= 1:
            for ce in self.result_list:
                tlist.append(ce.json())
        return json.dumps(tlist, ensure_ascii=False)
    
    def tantivy_json(self):
        tlist = []
        if len(self.result_list) >= 1:
            for ce in self.result_list:
                tlist.append(json.dumps(ce.json(), ensure_ascii=False) + "\n")
        return tlist
    
    def readable_json(self):
        tlist = []
        if len(self.result_list) >= 1:
            for ce in self.result_list:
                tlist.append(ce.json())
        return json.dumps(tlist, ensure_ascii=False, indent=4)



def main(filename, savename):
    astp = PythonASTParser(str(filename))
    result = astp.readable_json()
    # result = astp.tantivy_json()
    with open(savename, "w", encoding="utf8") as f:
        f.write(result)
        # f.writelines(result)

if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename, "test.json")

