from lark import Lark
from lark.visitors import Interpreter
import time
import random
import math
from sympy import *

variables = {}
functions = {}

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class ToMyLang(Interpreter):
    def __init__(self):
        self.scopes = [variables]
        self.functions = functions
        super().__init__()

    def _current_scope(self):
        return self.scopes[-1]

    def _get_var(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _set_var(self, name, value):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return
        self._current_scope()[name] = value

    # 負の数
    def negative(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        return 0 - num
    # 型
    def number(self, tree):
        num = tree.children[0]
        if '.' in num:
            return float(num)
        else:
            return int(num)
    def string(self, tree):
        return tree.children[0][1:-1]
    def boolean(self, tree):
        if (tree.children[0] == "true"):
            return True
        else:
            return False
    def value(self, tree):
        return self.visit(tree.children[0])
    def array(self, tree):
        result = []
        for child in tree.children:
            result.append(self._resolve(self.visit(child)))
        return result
    
    # 制御
    def wait(self, tree):
        if (type(self.visit(tree.children[0])) == bool):
            condition = tree.children[0]
            while not self.visit(condition):
                time.sleep(0.1)
        else:
            duration = self._resolve(self.visit(tree.children[0]))
            time.sleep(duration)
    def repeat(self, tree):
        if (type(self.visit(tree.children[0])) == bool):
            condition = tree.children[0]
            block = tree.children[1:]
            while not self.visit(condition):
                for cmd in block:
                    self.visit(cmd)
        elif (type(self.visit(tree.children[0])) == int):
            times = self._resolve(self.visit(tree.children[0]))
            block = tree.children[1:]
            for _ in range(times):
                for cmd in block:
                    self.visit(cmd)
    def forever(self, tree):
        while True:
            for cmd in tree.children:
                self.visit(cmd)
    def if_(self, tree):
        condition = self.visit(tree.children[0])
        then_block = tree.children[1]
        if len(tree.children) > 2:
            else_block = tree.children[2]
        else:
            else_block = None
        if condition:
            for cmd in then_block.children:
                self.visit(cmd)
        elif else_block:
            for cmd in else_block.children:
                self.visit(cmd)

    # 演算
    def add(self, tree):
        left = self._resolve(self.visit(tree.children[0]))
        right = self._resolve(self.visit(tree.children[1]))
        return left + right
    def subtract(self, tree):
        left = self._resolve(self.visit(tree.children[0]))
        right = self._resolve(self.visit(tree.children[1]))
        return left - right
    def multiply(self, tree):
        left = self._resolve(self.visit(tree.children[0]))
        right = self._resolve(self.visit(tree.children[1]))
        return left * right
    def divide(self, tree):
        left = self._resolve(self.visit(tree.children[0]))
        right = self._resolve(self.visit(tree.children[1]))
        return left / right
    def random(self, tree):
        start = self._resolve(self.visit(tree.children[0]))
        end = self._resolve(self.visit(tree.children[1]))
        if (type(start) == int and type(end) == int):
            return random.randint(start, end)
        else:
            return random.uniform(start, end)
    def equal(self, tree):
        left = self._resolve(self.visit(tree.children[0]))
        right = self._resolve(self.visit(tree.children[1]))
        return left == right
    def greater(self, tree):
        left = self._resolve(self.visit(tree.children[0]))
        right = self._resolve(self.visit(tree.children[1]))
        return left > right
    def less(self, tree):
        left = self._resolve(self.visit(tree.children[0]))
        right = self._resolve(self.visit(tree.children[1]))
        return left < right
    def and_(self, tree):
        left = self._resolve(self.visit(tree.children[0]))
        right = self._resolve(self.visit(tree.children[1]))
        return left and right
    def or_(self, tree):
        left = self._resolve(self.visit(tree.children[0]))
        right = self._resolve(self.visit(tree.children[1]))
        return left or right
    def not_(self, tree):
        value = self._resolve(self.visit(tree.children[0]))
        return not value
    def join(self, tree):
        left = str(self._resolve(self.visit(tree.children[0])))
        right = str(self._resolve(self.visit(tree.children[1])))
        if (type(self.visit(tree.children[0])) == str or type(self.visit(tree.children[1])) == str):
            return left + right
        elif (type(self.visit(tree.children[0])) == bool or type(self.visit(tree.children[1])) == bool):
            print("エラーじゃボケェ")
        else:
            return int(left + right)
    def letter(self, tree):
        index = self._resolve(self.visit(tree.children[0]))
        character = self._resolve(self.visit(tree.children[1]))
        if (type(character) == str and type(index) == int):
            if (index > len(character)):
                print("エラーじゃボケェ")
            elif (index < 1):
                print("エラーじゃボケェ")
            else:
                return character[index - 1]
        else:
            print("エラーじゃボケェ")
    def length(self, tree):
        character = self._resolve(self.visit(tree.children[0]))
        if (type(character) == int):
            character = str(character)
        if (type(character) == str):
            return len(character)
        else:
            print("エラーじゃボケェ")
    def contains(self, tree):
        character = self._resolve(self.visit(tree.children[0]))
        item = self._resolve(self.visit(tree.children[1]))
        if (type(character) == list):
            return item in character
        if ((type(character) == type(item)) or (isinstance(character, (int, float)) and isinstance(item, (int, float)))):
            if (isinstance(character, (int, float, str))):
                return str(item) in str(character)
            else:
                print("エラーじゃボケェ")
        else:
            print("エラーじゃボケェ")
    def mod(self, tree):
        left = self._resolve(self.visit(tree.children[0]))
        right = self._resolve(self.visit(tree.children[1]))
        return left % right
    def round(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        return round(num)
    def abs(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        return abs(num)
    def floor(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        return math.floor(num)
    def ceiling(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        return math.ceil(num)
    def sqrt(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        if (float(N(sqrt(num))).is_integer()):
            return int(N(sqrt(num)))
        else:
            return float(N(sqrt(num)))
    def sin(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        return float(N(sin(rad(num))))
    def cos(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        return float(N(cos(rad(num))))
    def tan(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        if (N(tan(rad(num))) == zoo):
            return None
        else:
            return float(N(tan(rad(num))))
    def asin(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        if (float(N(asin(num) * 180 / pi)).is_integer()):
            return int(N(asin(num) * 180 / pi))
        else:
            return float(N(asin(num) * 180 / pi))
    def acos(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        if (float(N(acos(num) * 180 / pi)).is_integer()):
            return int(N(acos(num) * 180 / pi))
        else:
            return float(N(acos(num) * 180 / pi))
    def atan(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        if (float(N(atan(num) * 180 / pi)).is_integer()):
            return int(N(atan(num) * 180 / pi))
        else:
            return float(N(atan(num) * 180 / pi))
    def ln(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        if (N(ln(num)) == zoo):
            return None
        else:
            return float(N(ln(num)))
    def log(self, tree):
        num = self._resolve(self.visit(tree.children[0]))
        if (N(log(num, 10)) == zoo):
            return None
        elif (float(N(log(num, 10))).is_integer()):
            return int(N(log(num, 10)))
        else:
            return float(N(log(num, 10)))
    def napier(self, tree):
        return N(exp(1))
    def pow(self, tree):
        right = self._resolve(self.visit(tree.children[0]))
        left = self._resolve(self.visit(tree.children[1]))
        return right ** left

    # 変数
    def var(self, tree):
        name = self.visit(tree.children[0])
        value = self.visit(tree.children[1])
        self._current_scope()[name] = value
    def assignment(self, tree):
        target = tree.children[0]
        name = str(target.children[0])
        if (target.children[1] != None):
            index = self._resolve(self.visit(target.children[1]))
            value = self._resolve(self.visit(tree.children[1]))

            self._get_var(name)[index - 1] = value
        else:
            value = self._resolve(self.visit(tree.children[1]))
            self._set_var(name, value)
    def var_name(self, tree):
        if (tree.children[0] == "true" or tree.children[0] == "false"):
            print("エラーじゃボケェ")
        else:
            name = str(tree.children[0])
            if tree.children[1] == None:
                return name
            else:
                index = self._resolve(self.visit(tree.children[1]))
                return self._get_var(name)[index - 1]
    def _resolve(self, v):
        if (type(v) == str):
            value = self._get_var(v)
            if value is not None:
                return value
        return v
    
    # リスト
    def append(self, tree):
        name = self.visit(tree.children[0])
        value = self._resolve(self.visit(tree.children[1]))
        self._get_var(name).append(value)
    def delete(self, tree):
        name = self.visit(tree.children[0])
        if (len(tree.children) == 1):
            self._get_var(name).clear()
        else:
            index = self._resolve(self.visit(tree.children[1]))
            self._get_var(name).pop(index - 1)
    def insert(self, tree):
        name = self.visit(tree.children[0])
        value = self._resolve(self.visit(tree.children[1]))
        index = self._resolve(self.visit(tree.children[2]))
        self._get_var(name).insert(index - 1, value)
    def item(self, tree):
        name = self.visit(tree.children[0])
        value = self._resolve(self.visit(tree.children[1]))
        item = self._get_var(name).index(value)
        return item + 1
    def length_list(self, tree):
        name = self.visit(tree.children[0])
        return len(self._get_var(name))
    
    # 関数
    def define(self, tree):
        name = str(tree.children[0])
        params = []
        body_start = 1

        if len(tree.children) > 1 and getattr(tree.children[1], "data", None) == "param_list":
            params = [str(param) for param in tree.children[1].children]
            body_start = 2
        elif len(tree.children) > 1 and tree.children[1] is None:
            body_start = 2

        self.functions[name] = {
            "params": params,
            "body": tree.children[body_start:]
        }

    def function_call(self, tree):
        name = str(tree.children[0])
        if name not in self.functions:
            print("エラーじゃボケェ")
            return None

        fn = self.functions[name]
        args = []
        if len(tree.children) > 1 and tree.children[1] is not None:
            args = [self._resolve(self.visit(arg)) for arg in tree.children[1].children]

        if len(args) != len(fn["params"]):
            print("エラーじゃボケェ")
            return None

        local_scope = dict(zip(fn["params"], args))
        self.scopes.append(local_scope)
        try:
            for cmd in fn["body"]:
                self.visit(cmd)
        except ReturnSignal as signal:
            return signal.value
        finally:
            self.scopes.pop()

        return None

    def return_(self, tree):
        value = self._resolve(self.visit(tree.children[0]))
        raise ReturnSignal(value)

    # 出力
    def print_(self, tree):
        value = self._resolve(self.visit(tree.children[0]))
        print(value)

if __name__ == "__main__":
    parser = Lark(
        open("/Users/ono/Desktop/Clambon/Lark_lesson/Clambon/grammar.lark").read(),
        parser="lalr"
    )

    program = open("/Users/ono/Desktop/Clambon/Lark_lesson/Clambon/program.txt").read()
    tree = parser.parse(program)

    interpreter = ToMyLang()
    interpreter.visit(tree)
