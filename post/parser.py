import ply.yacc as yacc
from lexer import tokens
import random

class Expression:
    def __init__(self, value, detailed_result):
        self.value = value
        self.detailed_result = detailed_result

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression'''
    if p[2] == '+':
        value = p[1].value + p[3].value
    elif p[2] == '-':
        value = p[1].value - p[3].value
    elif p[2] == '*':
        value = p[1].value * p[3].value
    elif p[2] == '/':
        value = p[1].value / p[3].value
    elif p[2] == '==':
        value = p[1].value == p[3].value
    elif p[2] == '!=':
        value = p[1].value != p[3].value
    elif p[2] == '<':
        value = p[1].value < p[3].value
    elif p[2] == '<=':
        value = p[1].value <= p[3].value
    elif p[2] == '>':
        value = p[1].value > p[3].value
    elif p[2] == '>=':
        value = p[1].value >= p[3].value
    p[0] = Expression(value, f'{p[1].detailed_result} {p[2]} {p[3].detailed_result}')

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]
    p[0].detailed_result = f'({p[2].detailed_result})'

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = Expression(p[1], str(p[1]))

def p_expression_dice(p):
    '''expression : DICE
                  | DICE_CONDITION'''
    if 'b' in p[1]:
        if '>=' in p[1]:
            num_dice, rest = p[1].split('b')
            num_sides, condition = rest.split('>=')
            num_dice, num_sides, condition = int(num_dice), int(num_sides), int(condition)
            results = [random.randint(1, num_sides) for _ in range(num_dice)]
            success_count = sum(1 for r in results if r >= condition)
            p[0] = Expression(success_count, f'{results} 成功数{success_count}')
        else:
            num_dice, num_sides = map(int, p[1].split('b'))
            results = [random.randint(1, num_sides) for _ in range(num_dice)]
            p[0] = Expression(results, f'{results}')
    else:
        num_dice, num_sides = map(int, p[1].split('d'))
        results = [random.randint(1, num_sides) for _ in range(num_dice)]
        p[0] = Expression(sum(results), f'{sum(results)}[{",".join(map(str, results))}]')

def p_error(p):
    print(f"Syntax error at '{p.value}'")

parser = yacc.yacc()
