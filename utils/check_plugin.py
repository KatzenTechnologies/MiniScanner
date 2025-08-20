import ast
import string

def get_assign_targets(node, deproxy):
    if len(node.targets) == 1:
        if isinstance(node.targets[0], ast.Name):
            return [[node.targets[0].id], node.value]

        if isinstance(node.targets[0], ast.Tuple) or isinstance(node.targets[0], ast.List):
            return [[i.id for i in node.targets[0].elts], node.value]

        if isinstance(node.targets[0], ast.Subscript):
            if isinstance(node.targets[0].value, ast.Call):
                if isinstance(node.targets[0].value.func, ast.Name):
                    if node.targets[0].value.func.id in ["globals", "locals"] \
                        or deproxy.get(node.targets[0].value.func.id) in ["globals", "locals"]:
                        if isinstance(node.targets[0].slice, ast.Constant):
                            return [[node.targets[0].slice.value], node.value]
                        if isinstance(node.targets[0].slice, ast.Name):
                            if deproxy.get(node.targets[0].slice.id) is not None:
                                return [[deproxy.get(node.targets[0].slice.id)], node.value]
                            else:
                                return None

def get_assign_values(node, deproxy):
    if isinstance(node, ast.Subscript):
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            func = node.value.func.id
            if func in ["globals", "locals"] or deproxy.get(func) in ["globals", "locals"]:
                if isinstance(node.slice, ast.Constant):
                    return node.slice.value
                elif isinstance(node.slice, ast.Name):
                    resolved = deproxy.get(node.slice.id)
                    if resolved:
                        return resolved
    elif isinstance(node, (ast.Tuple, ast.List)):
        return [get_assign_values(e, deproxy) for e in node.elts]
    return node

class Deproxy(ast.NodeVisitor):
    def __init__(self, verbose=False):
        self.vars = {}
        self.verbose = verbose

        super().__init__()

    def visit_Assign(self, node):

        targets = get_assign_targets(node, self.vars)
        if targets is None:
            if self.verbose:
                print(f"Некорректная или неподдерживаемая конструкция, не обратываю: {ast.dump(node)}")
            return
        names, value_node = targets
        values = get_assign_values(value_node, self.vars)

        if isinstance(values, list) and len(values) == len(names):
            for name, val in zip(names, values):
                self.vars[name] = val
        elif len(names) == 1:
            self.vars[names[0]] = values
        else:
            pass

# Constructing classes to parse classes and functions cuz im lazy to parse bodies + we need to check function names!
class DeproxySub(ast.NodeVisitor):
    def __init__(self):
        self.vars = {}
        self.just_for_check = []
        super().__init__()
    def visit_FunctionDef(self, node):
        self.vars.update({node.name: node})
        for i in node.args.args:
            self.just_for_check.append(i.arg)
        return node

    def visit_ClassDef(self, node):
        self.vars.update({node.name: node})

class VariableChecker:
    def __init__(self, base=None):
        self.detected = False

        if base is None:
            self.base = [
                ["o", "0"],
                ["j","i","l"],
                ["m",'n'],
                ["Z","2"],
                ["l","1"]
            ]

        self.normal_vars = string.ascii_lowercase + string.ascii_uppercase + string.digits + "_"
        self.max_length = 30 # mnogo false detectov

    def check(self, value):
        symbols = list(set(list(value.lower())))
        if symbols in self.base or\
            not all([i in self.normal_vars for i in value]) or \
            (symbols == ["_"] and not value == "_"):
            return True
        return False

class CallsChecker(ast.NodeVisitor):
    def __init__(self, deproxy):
        self.deproxy = deproxy
        self.detected = False
        self.bad_funcs = ["exec","eval","compile"]
        super().__init__()

    def visit_Call(self, node):
        # Should be replaced ASAP

        val = get_assign_values(node.func, self.deproxy)
        if isinstance(val, ast.Name):
            if val.id in self.bad_funcs:
                self.detected = True

        return node

def is_obfuscated(file):
    variablechecker = VariableChecker()
    code = file.read()
    file.close()
    parsed = ast.parse(code)

    deproxysub = DeproxySub()
    deproxysub.visit(parsed)

    deproxy = Deproxy()
    deproxy.vars = deproxysub.vars
    deproxy.visit(parsed)

    detected = False
    for i in deproxysub.just_for_check + list(deproxy.vars.keys()):
        if variablechecker.check(i):
            detected = True
            break

    if detected:
        return True

    calls = CallsChecker(deproxy)
    calls.visit(parsed)
    if calls.detected:
        return True

    return False
