import itertools
from sympy import Symbol, parse_expr
import json

op_add = ['+','-']
op_prod = ['*','/']

def generate_operations():
    op_permutations = list()

    # Iterates through all permutations of operations
    # Assigns parenthesis sets if order of operations will be affected
    # see add_parentheses() for different patterns
    for op in itertools.product(op_add + op_prod, repeat=3):
        op_paren = [0] # no parentheses, default case
        if op[0] in op_add:
            if op[2] in op_prod:
                op_paren.append(1)
            if op[1] in op_prod:
                op_paren.append(2)
                if op[2] in op_add:
                    op_paren.append(4)
            elif op[1] in op_add and op[2] in op_prod:
                op_paren.append(3)
        if op[0] in op_prod:
            if op[1] in op_add:
                op_paren.append(3)
                op_paren.append(5)
                if op[2] in op_prod:
                    op_paren.append(1)
            elif op[2] in op_add:
                op_paren.append(4)
                op_paren.append(5)
        
        op_permutations.append((op, op_paren))

    return op_permutations

def to_postfix(expr):
    postfix = []
    op_stack = list()
    for x in expr:
        if x in ['a','b','c','d']:
            postfix.append(x)
        elif x in op_add:
            if len(op_stack) and op_stack[-1] != '(':
                postfix.append(op_stack.pop())
            op_stack.append(x)
        elif x in op_prod:
            if len(op_stack) and op_stack[-1] in op_prod:
                postfix.append(op_stack.pop())
            op_stack.append(x)
        elif x == '(':
            op_stack.append(x)
        elif x == ')':
            while op_stack[-1] != '(':
                postfix.append(op_stack.pop())
            op_stack.pop()
    while len(op_stack):
        postfix.append(op_stack.pop())

    return ''.join(postfix)

def add_parentheses(eq_array, paren_set):
    if paren_set == 1:
        # Pattern 1: ( X _ X _ X ) _ X
        return ['('] + eq_array[:5] + [')'] + eq_array[5:]
    elif paren_set == 2:
        # Pattern 2: ( X _ X ) _ X _ X
        return ['('] + eq_array[:3] + [')'] + eq_array[3:]
    elif paren_set == 3:
        # Pattern 3: X _ ( X _ X ) _ X
        return eq_array[:2] + ['('] + eq_array[2:5] + [')'] + eq_array[5:]
    elif paren_set == 4:
        # Pattern 4: X _ X _ ( X _ X )
        return eq_array[:4] + ['('] + eq_array[4:] + [')']
    elif paren_set == 5:
        # Pattern 5: X _ ( X _ X _ X )
        return eq_array[:2] + ['('] + eq_array[2:] + [')']
    return eq_array

def generate_equations(operations, input_vals = ['a','b','c','d'], split = False):
    eq_symbols = {
        'a': Symbol('a', positive=True),
        'b': Symbol('b', positive=True),
        'c': Symbol('c', positive=True),
        'd': Symbol('d', positive=True)
        }

    equations = list()
    unique_eqs = set()
    permutations = set()
    postfix = list()

    # iterate through all permutations of input numbers
    # add every operation set to each permutation
    # iterate over each parenthesis set in op_set[1]
    # parse each equation into sympy expression
    # add expression to set if does not exist
    for p in itertools.permutations(input_vals):
        # avoid duplicates if there are repeated numbers
        if p in permutations:
            continue
        permutations.add(p)

        for op_set in operations:
            eq_iter = itertools.zip_longest(p, op_set[0])
            eq_array = [val for expr in eq_iter for val in expr if val is not None]
            for paren_idx in op_set[1]:
                eq_a = add_parentheses(eq_array, paren_idx)
                eq_str = ''.join(eq_a)
                eq_sym = parse_expr(eq_str, eq_symbols)
                if eq_sym not in unique_eqs:
                    print(eq_sym)
                    # filter out a few known incorrect equations
                    # e.g. a-a*a-a (-3*a); a/a*a/a (1); a-b/(c-c) (a-b/0)
                    if eq_sym.is_nonpositive or eq_sym.is_integer or eq_sym.is_infinite:
                        continue
                    eq_postfix = to_postfix(eq_a)
                    unique_eqs.add(eq_sym)
                    if split:
                        equations.append(eq_str)
                        postfix.append(eq_postfix)
                    else:
                        equations.append([eq_str, eq_postfix])
    return (equations, postfix)

def generate_equation_map():
    operations = generate_operations()
    # if true, split postfix and equations into separate arrays
    # default is False
    split = True
    # all possible permutations of 4-digit number
    input_perms = [ ['a','a','a','a'], ['a','a','a','b'], ['a','a','b','b'], ['a','a','b','c'], ['a','b','c','d'] ]
    json_obj = dict()
    for perm in input_perms:
        (eq_set, pf_set) = generate_equations(operations, perm, split)
        eq_key = 'eq_' + ''.join(perm)
        if split:
            pf_key = 'pf_' + ''.join(perm)
            json_obj.update({ pf_key: pf_set })
        json_obj.update({ eq_key: eq_set })

    f = open('./equation_map.json', 'w')
    json.dump(json_obj, f, separators=(',',':'))
    f.close()

# quick and dirty solution with no input sanitation
# input_num should be string e.g. "1234"
# target should be desired result - 10 in this case
def solve_problem(input_num, target):
    # generate a pattern and value map
    symbols = ['a','b','c','d']
    dupes = dict()
    for n in input_num:
        if dupes.get(n):
            dupes[n] += 1
        else:
            dupes[n] = 1
    pattern = ''
    val_map = dict()
    for (i, val) in enumerate(sorted(dupes.keys(), key=lambda x: dupes[x], reverse=True)):
        val_map[symbols[i]] = val
        pattern += symbols[i] * dupes[val]

    # load equations from json
    f = open('./equation_map.json',)
    eq_map = json.load(f)
    eq_list = list(eq_map['eq_'+pattern])
    f.close()

    # evaluate each equation
    # check result against `target`
    # return solutions
    solutions = list()
    for eq in eq_list:
        parsed_eq = ''.join(list(map(lambda x: val_map[x] if x in ['a','b','c','d'] and val_map.get(x) else x, eq)))
        try:
            if eval(parsed_eq) == target:
                solutions.append(parsed_eq)
        except(ZeroDivisionError):
            continue
    return solutions

generate_equation_map()
# solutions = solve_problem("1199", 10)
# print(len(solutions))