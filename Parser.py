import re

# Token types
TOKEN_VARIABLE = 'VARIABLE'
TOKEN_NUMBER = 'NUMBER'
TOKEN_STRING_LITERAL = 'STRING'
TOKEN_ASSIGNMENT = 'ASSIGNMENT'
TOKEN_IF = 'IF'
TOKEN_ELSE = 'ELSE'
TOKEN_WHILE = 'WHILE'
TOKEN_FOR = 'FOR'
TOKEN_PLUS = 'PLUS'
TOKEN_MINUS = 'MINUS'
TOKEN_MULTIPLY = 'MULTIPLY'
TOKEN_DIVIDE = 'DIVIDE'
TOKEN_EQUALS = 'EQUALS'
TOKEN_NOT_EQUALS = 'NOT_EQUALS'
TOKEN_LESS_THAN = 'LESS_THAN'
TOKEN_LESS_EQUALS = 'LESS_EQUALS'
TOKEN_GREATER_THAN = 'GREATER_THAN'
TOKEN_GREATER_EQUALS = 'GREATER_EQUALS'
TOKEN_OPEN_PAREN = 'OPEN_PAREN'
TOKEN_CLOSE_PAREN = 'CLOSE_PAREN'
TOKEN_OPEN_BRACE = 'OPEN_BRACE'
TOKEN_CLOSE_BRACE = 'CLOSE_BRACE'
TOKEN_COLON = 'COLON'
TOKEN_DO = 'DO'
TOKEN_PRINT = 'PRINT'
TOKEN_THEN = 'THEN'
TOKEN_IN = 'IN'
TOKEN_FUNCTION = 'FUNCTION'
TOKEN_COMMA = 'COMMA'
TOKEN_RETURN = 'RETURN'

# Token regular expressions
TOKENS_REGEX = [
    (r'[-]?\d+[\.\d+]?', TOKEN_NUMBER),
    (r'<-', TOKEN_ASSIGNMENT),
    (r'if', TOKEN_IF),
    (r'else', TOKEN_ELSE),
    (r'while', TOKEN_WHILE),
    (r'for', TOKEN_FOR),
    (r'\+', TOKEN_PLUS),
    (r'-', TOKEN_MINUS),
    (r'\*', TOKEN_MULTIPLY),
    (r'/', TOKEN_DIVIDE),
    (r'==', TOKEN_EQUALS),
    (r'!=', TOKEN_NOT_EQUALS),
    (r'<', TOKEN_LESS_THAN),
    (r'<=', TOKEN_LESS_EQUALS),
    (r'>', TOKEN_GREATER_THAN),
    (r'>=', TOKEN_GREATER_EQUALS),
    (r'\(', TOKEN_OPEN_PAREN),
    (r'\)', TOKEN_CLOSE_PAREN),
    (r'\[', TOKEN_OPEN_BRACE),
    (r'\]', TOKEN_CLOSE_BRACE),
    (r':', TOKEN_COLON),
    (r'do', TOKEN_DO),
    (r'print', TOKEN_PRINT),
    (r'then', TOKEN_THEN),
    (r'in', TOKEN_IN),
    (r'function', TOKEN_FUNCTION),
    (r'return', TOKEN_RETURN),
    (r',', TOKEN_COMMA),
    (r'".*"', TOKEN_STRING_LITERAL),
    (r'[a-zA-Z_][a-zA-Z_0-9]*', TOKEN_VARIABLE)
]

#function for debugging
def printTokens(tokens):

    print("-----PRINT-----")

    for token in tokens:
        print(token)


# LEXER

#turns the input string into tokens for the parser to use
#this is the first function called to initialize the parser,
#and to make sure all symbols are valid
def tokenize(input_string):
    tokens = []
    while input_string:
        for pattern, token_type in TOKENS_REGEX:
            match = re.match(pattern, input_string)
            if match:
                value = match.group(0)
                #if token_type == TOKEN_VARIABLE:
                #    token_type = checkKeywords(value)
                tokens.append((token_type, value))
                input_string = input_string[len(value):].strip()
                break
        else:
            raise ValueError(f"ERROR: Invalid character '{input_string[0]}' detected in input string")
    #for debugging
    #printTokens(tokens)
    return tokens

#PARSER

def parseVariable(tokens):
    if tokens[0][0] == TOKEN_VARIABLE:
        print(str(tokens[0][1]) + " is a var")
        return tokens.pop(0)[1]
    else:
        printTokens(tokens[0])
        raise ValueError("Expected variable name")

def parseNumber(tokens):
    if tokens[0][0] == TOKEN_NUMBER:
        return int(tokens.pop(0)[1])
    else:
        printTokens(tokens[0])
        raise ValueError("Expected number")

# parseExpression, Term, and Factor are ordered in such a way that
# it maintains order of operations.
# starting with + and - operations
# also checks for function calls here
def parseExpression(tokens):
    if(len(tokens) > 1):
        if(tokens[1][0] == TOKEN_OPEN_PAREN):
            return parseFunctionCall(tokens)
        elif(tokens[1][0] == TOKEN_COMMA):
            return tokens.pop(0)[1]
    term1 = parseTerm(tokens)
    while tokens and tokens[0][0] in (TOKEN_PLUS, TOKEN_MINUS):
        operator = tokens.pop(0)[1] #add or subtract operator
        term2 = parseTerm(tokens)
        if operator == '+':
            return f"{term1} + {term2}"
        elif operator == '-':
            return f"{term1} - {term2}"
    return term1

# * and / operations
def parseTerm(tokens):
    factor1 = parseFactor(tokens)
    while tokens and tokens[0][0] in (TOKEN_MULTIPLY, TOKEN_DIVIDE):
        operator = tokens.pop(0)[1] #multiply or divide operator
        factor2 = parseFactor(tokens)
        notCompatible = not isinstance(factor1, str) and not isinstance(factor2, str)
        if operator == '*':
            if notCompatible:
                raise ValueError("Incompatible data type in '*' operation")
            return f"{factor1} * {factor2}"
        elif operator == '/':
            if notCompatible:
                raise ValueError("Incompatible data type in '/' operation")
            return f"{factor1} / {factor2}"
    return factor1

# anything in parenthesis - recursively calls expression function
# # OR
# string literals, numbers, variables, etc
def parseFactor(tokens):
    if tokens[0][0] == TOKEN_OPEN_PAREN:
        tokens.pop(0)
        expression = parseExpression(tokens)
        if tokens[0][0] == TOKEN_CLOSE_PAREN:
            tokens.pop(0)
            return expression
        else:
            printTokens(tokens[0])
            raise ValueError("Expected closing parenthesis")
    elif tokens[0][0] == TOKEN_STRING_LITERAL:
        return f"{tokens[0][1]}"
    elif tokens[0][0] == TOKEN_NUMBER:
        return parseNumber(tokens)
    elif tokens[0][0] == TOKEN_VARIABLE:
        return parseVariable(tokens)
    else:
        printTokens(tokens[0])
        raise ValueError("Expected expression")

# same as python: '({expression} {operator} {expression})'
def parseCondition(tokens):
    print("Parsing condition")
    tokens.pop(0)
    left_expression = parseExpression(tokens)
    printTokens(tokens)
    operator = tokens.pop(0)[1]  #comparison operator
    right_expression = parseExpression(tokens)
    tokens.pop(0)
    return f"({left_expression} {operator} {right_expression})"

# using '<-' as the data going towards the variable (in memory)
def parseAssignmentStatement(tokens):
    variable = parseVariable(tokens)
    if tokens[0][0] == TOKEN_ASSIGNMENT:
        tokens.pop(0)  #'<-' token
        expression = parseExpression(tokens)
        return f"{variable} = {expression}"
    else:
        printTokens(tokens[0])
        raise ValueError("Expected assignment operator")

# format: if {condition} then do {statement} else do {statement}
def parseIfStatement(tokens):
    tokens.pop(0)  # 'if' token
    condition = parseCondition(tokens)
    if tokens[0][0] == TOKEN_THEN:
        tokens.pop(0) # 'then' token
        if tokens[0][0] == TOKEN_DO:
            tokens.pop(0)  # 'do' token
            body = parseStatement(tokens)
            if tokens[0][0] == TOKEN_ELSE:
                tokens.pop(0)  # 'else' token
                if tokens[0][0] == TOKEN_DO:
                    tokens.pop(0)  # 'do' token
                    else_body = parseStatement(tokens)
                    return f"if {condition} then do\n\t{body}\nelse do\n\t{else_body}"
                else:
                    printTokens(tokens[0])
                    raise ValueError("Expected 'do' after 'else'")
            return f"if {condition} then do\n{body}"
        else:
            printTokens(tokens[0])
            raise ValueError("Expected 'do' after if statement")
    else:
        printTokens(tokens[0])
        raise ValueError("Expected 'then' after condition")
    
# format: while {condition} do {body}
def parseWhileLoop(tokens):
    tokens.pop(0)  # 'while' token
    condition = parseCondition(tokens)
    if tokens[0][0] == TOKEN_DO:
        tokens.pop(0) # 'do' token
        body = parseStatement(tokens)
        return f"while {condition} do \n\t{body}"
    else:
        raise ValueError("Expected 'do' at the end of while loop")

# format: do {body} while {condition}
def parseDoWhileLoop(tokens):
    tokens.pop(0) # 'do' token
    body = parseStatement(tokens)
    if tokens[0][0] == TOKEN_WHILE:
        tokens.pop(0)  # 'if' token
        condition = parseCondition(tokens)
        return f"do\n\t{body}\nwhile {condition}"
    else:
        raise ValueError("Expected 'while' at the end of do-while loop")


# different formats
# for a range: for {iterator} in ({lower bound expression}:{increment expression}:{upperbound expression}) do {body}
# for specific values: for {iterator} in [{number} {number} ... {number}] do {body}
def parseForLoop(tokens):
    tokens.pop(0) # 'for' token
    if tokens[0][0] == TOKEN_VARIABLE:
        iterator = parseVariable(tokens)
        if tokens[0][0] == TOKEN_IN:
            tokens.pop(0) # 'in' token
            #range
            if tokens[0][0] == TOKEN_OPEN_PAREN:
                tokens.pop(0) # '(' token
                lower_bound = parseExpression(tokens)
                if tokens[0][0] == TOKEN_COLON:
                    tokens.pop(0) # ':' token
                    increment = parseExpression(tokens)
                    if tokens[0][0] == TOKEN_COLON:
                        tokens.pop(0) # ':' token
                        upper_bound = parseExpression(tokens)
                        if tokens[0][0] == TOKEN_CLOSE_PAREN:
                            tokens.pop(0) # ')' token
                            if tokens[0][0] == TOKEN_DO:
                                tokens.pop(0) # 'do' token
                                body = parseStatement(tokens)
                                return f"for {iterator} in ({lower_bound}:{increment}:{upper_bound}) do \n\t{body}"
                            else:
                                raise ValueError("Expected 'do' after for loop")
                        else:
                            raise ValueError("Expected closed parenthesis")
                    else:
                        raise ValueError("Missing colon after increment")
                else:
                    raise ValueError("Missing colon after lower bound")
            #specific values
            elif tokens[0][0] == TOKEN_OPEN_BRACE:
                tokens.pop(0) # '[' token
                values = []
                print("WHILE LOOP")
                while tokens[0][0] == TOKEN_NUMBER:
                    printTokens(tokens[0])
                    printTokens(tokens[1])
                    values.append(parseNumber(tokens))
                    if tokens[0][0] == TOKEN_COMMA:
                        tokens.pop(0) # ',' token
                if tokens[0][0] == TOKEN_CLOSE_BRACE:
                    tokens.pop(0) # ']' token
                    if tokens[0][0] == TOKEN_DO:
                        tokens.pop(0) # 'do' token
                        body = parseStatement(tokens)
                        return f"for {iterator} in [{','.join(str(num) for num in values)}] do \n\t{body}"
                    else:
                        raise ValueError("Expected 'do' after for loop")
                else:
                    raise ValueError("Expected closing brace")
            else:
                raise ValueError("Invalid range of 'for' loop")
        else:
            raise ValueError("Expected 'in' after iterator")
    else:
        raise ValueError("Expected iterator after 'for'")

# format: {function name}({arguments})
def parseFunctionCall(tokens):
    if tokens[0][0] == TOKEN_VARIABLE:
        print("Parsing function name:" + str(tokens[0]))
        variable = parseVariable(tokens)
        print("Next: " + str(tokens[0]))
        if tokens[0][0] == TOKEN_OPEN_PAREN:
            tokens.pop(0)  # '(' token
            print("Open parenthesis popped")
            arguments = []
            while tokens and tokens[0][0] != TOKEN_CLOSE_PAREN:
                arguments.append(parseExpression(tokens))
                if tokens[0][0] == TOKEN_COMMA:
                    tokens.pop(0)  # ',' token
            print(tokens[0])
            if tokens[0][0] == TOKEN_CLOSE_PAREN:
                tokens.pop(0)  # ')' token
                print("Closed parenthesis popped")
                functionCall = f"{variable}("
                for index in range(len(arguments)-1):
                    functionCall += f"{arguments[index]},"
                functionCall += f"{arguments[-1]})"
                return functionCall
            else:
                printTokens(tokens[0])
                raise ValueError("Expected closing parenthesis after function call arguments")
        else:
            printTokens(tokens[0])
            raise ValueError("Expected open parenthesis")
    else:
        printTokens(tokens[0])
        raise ValueError("Expected function call")

# Function definition
# format: function {name}({parameters}) do
def parseFunction(tokens):
    tokens.pop(0) #'function' call
    if tokens[0][0] == TOKEN_VARIABLE:
        func_name = tokens.pop(0)[1]
        if tokens[0][0] == TOKEN_OPEN_PAREN:
            tokens.pop(0)  # '(' token
            parameters = []
            while tokens[0][0] == TOKEN_VARIABLE:
                parameters.append(tokens.pop(0)[1])
                if tokens[0][0] == TOKEN_COMMA:
                    tokens.pop(0)  # ',' token
            if tokens[0][0] == TOKEN_CLOSE_PAREN:
                tokens.pop(0)  # ')' token
                if tokens[0][0] == TOKEN_DO:
                    tokens.pop(0)  # 'do' token
                    function_body = parseStatement(tokens)
                    return f"function {func_name}({', '.join(parameters)}) do\n\t{function_body}"
                else:
                    printTokens(tokens[0])
                    raise ValueError("Expected 'do' after function parameters")
            else:
                printTokens(tokens[0])
                raise ValueError("Expected closing parenthesis after function parameters")
        else:
            printTokens(tokens[0])
            raise ValueError("Expected opening parenthesis after function name")
    else:
        printTokens(tokens[0])
        raise ValueError("Expected function name")

# format: print({body})
def parsePrintStatement(tokens):
    tokens.pop(0) # 'print' token
    if tokens[0][0] == TOKEN_OPEN_PAREN:
        tokens.pop(0)  # '(' token
        body = parseExpression(tokens)
        if tokens[0][0] == TOKEN_CLOSE_PAREN:
            tokens.pop(0) # ')' token
            return f"print({body})"
        else:
            raise ValueError("Expected closing parenthesis")
    else:
        raise ValueError("Expected open parenthesis")

# for everything else; functions, if statements, for/while loops, etc
def parseStatement(tokens):
    print("Parsing statement:" + str(tokens[0]))
    if tokens[0][0] == TOKEN_VARIABLE:
        print("Parsing var:" + str(tokens[0]))
        variable = parseVariable(tokens)
        if tokens[0][0] == TOKEN_ASSIGNMENT:
            print("Parsing assignment")
            tokens.pop(0)  # '<-' token
            expression = parseExpression(tokens)
            return f"{variable} <- {expression}"
        elif tokens[0][0] == TOKEN_OPEN_PAREN:
            print("Parsing open parenthesis")
            tokens.pop(0)  # '(' token
            arguments = []
            while tokens and tokens[0][0] != TOKEN_CLOSE_PAREN:
                arguments.append(parseExpression(tokens))
                if tokens[0][0] == TOKEN_COMMA:
                    tokens.pop(0)  # ',' token
                else:
                    raise ValueError("Expected comma in arguments")
            if tokens[0][0] == TOKEN_CLOSE_PAREN:
                tokens.pop(0)  # ')' token
                return f"{variable}({', '.join(arguments)})"
            else:
                printTokens(tokens[0])
                raise ValueError("Expected closing parenthesis after function call arguments")
        else:
            raise ValueError("Expected assignment or function call")
    elif tokens[0][0] == TOKEN_FUNCTION:
        return parseFunction(tokens)
    elif tokens[0][0] == TOKEN_IF:
        return parseIfStatement(tokens)
    elif tokens[0][0] == TOKEN_WHILE:
        return parseWhileLoop(tokens)
    elif tokens[0][0] == TOKEN_FOR:
        return parseForLoop(tokens)
    elif tokens[0][0] == TOKEN_DO:
        return parseDoWhileLoop(tokens)
    elif tokens[0][0] == TOKEN_PRINT:
        return parsePrintStatement(tokens)
    elif tokens[0][0] == TOKEN_RETURN:
        tokens.pop(0) #'return' statement
        result = parseExpression(tokens)
        return f"\treturn {result}"
    else:
        print("Error: " + str(tokens[0]))
        raise ValueError("Expected assignment or if statement")

#begin here
def parseProgram(tokens):
    program = ""
    while tokens:
        statement = parseStatement(tokens)
        program += statement + "\n"
    return program

#Test the parser with valid input
print("Example 1:")

sample_code = """function add(x, y) do
    z <- x + y
    return z

result <- add(2, 3)

print(result)
"""

try:
    tokens = tokenize(sample_code)
    parsed_program1 = parseProgram(tokens)

    print("---------Parsed Program---------")
    print(parsed_program1)
    
except ValueError as err:
    print(err.args[0])