"""
OpenQASM 3.0 Parser Module

This module provides parsing functionality for OpenQASM 3.0 source code.
Implements a recursive descent parser that builds an Abstract Syntax Tree (AST).

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

from typing import List, Optional, Union, Dict, Any
from .lexer import QASMLexer, Token, TokenType
from .ast_nodes import *

class ParseError(Exception):
    """Exception raised for parsing errors."""
    
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parse error at line {token.line}, column {token.column}: {message}")

class QASMParser:
    """OpenQASM 3.0 recursive descent parser."""
    
    def __init__(self):
        self.tokens: List[Token] = []
        self.current = 0
        self.lexer = QASMLexer()
    
    def parse(self, source: str) -> Program:
        """
        Parse OpenQASM 3.0 source code into an AST.
        
        Args:
            source: OpenQASM 3.0 source code string
            
        Returns:
            Program AST node
            
        Raises:
            ParseError: If parsing fails
        """
        self.tokens = self.lexer.tokenize(source)
        self.current = 0
        
        # Remove comments and newlines for easier parsing
        self.tokens = [t for t in self.tokens if t.type not in [TokenType.COMMENT, TokenType.NEWLINE]]
        
        try:
            return self._parse_program()
        except IndexError:
            raise ParseError("Unexpected end of input", self._peek())
    
    def _peek(self, offset: int = 0) -> Token:
        """Peek at token at current position + offset."""
        pos = self.current + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF token
        return self.tokens[pos]
    
    def _advance(self) -> Token:
        """Consume and return current token."""
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _is_at_end(self) -> bool:
        """Check if we're at end of tokens."""
        return self._peek().type == TokenType.EOF
    
    def _previous(self) -> Token:
        """Return previous token."""
        return self.tokens[self.current - 1]
    
    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type."""
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _match(self, *types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of expected type or raise error."""
        if self._check(token_type):
            return self._advance()
        
        current_token = self._peek()
        raise ParseError(f"{message}. Got {current_token.type.name}", current_token)
    
    def _parse_program(self) -> Program:
        """Parse the entire program."""
        # Parse version declaration
        version_token = self._consume(TokenType.OPENQASM, "Expected 'OPENQASM'")
        version = self._consume(TokenType.FLOAT, "Expected version number").value
        self._consume(TokenType.SEMICOLON, "Expected ';' after version")
        
        # Parse includes
        includes = []
        while self._check(TokenType.INCLUDE):
            includes.append(self._parse_include())
        
        # Parse statements
        statements = []
        while not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return Program(
            version=version,
            includes=includes,
            statements=statements,
            line=version_token.line,
            column=version_token.column
        )
    
    def _parse_include(self) -> IncludeStatement:
        """Parse include statement."""
        include_token = self._consume(TokenType.INCLUDE, "Expected 'include'")
        filename = self._consume(TokenType.STRING, "Expected filename string").value
        self._consume(TokenType.SEMICOLON, "Expected ';' after include")
        
        # Remove quotes from filename
        filename = filename.strip('"\'')
        
        return IncludeStatement(
            filename=filename,
            line=include_token.line,
            column=include_token.column
        )
    
    def _parse_statement(self) -> Optional[Statement]:
        """Parse a statement."""
        try:
            # Variable declarations (with optional const)
            if self._check(TokenType.CONST):
                return self._parse_const_declaration()
            elif self._check(TokenType.QUBIT) or self._check(TokenType.BIT) or \
                 self._check(TokenType.INT) or self._check(TokenType.UINT) or \
                 self._check(TokenType.FLOAT_KW) or self._check(TokenType.ANGLE) or \
                 self._check(TokenType.BOOL):
                return self._parse_variable_declaration()
            
            # Control flow
            elif self._check(TokenType.IF):
                return self._parse_if_statement()
            elif self._check(TokenType.FOR):
                return self._parse_for_statement()
            
            # Quantum statements
            elif self._check(TokenType.GATE):
                return self._parse_gate_definition()
            elif self._check(TokenType.MEASURE):
                return self._parse_measurement()
            elif self._check(TokenType.RESET):
                return self._parse_reset()
            elif self._check(TokenType.BARRIER):
                return self._parse_barrier()
            
            # Gate modifiers
            elif self._check(TokenType.CTRL) or self._check(TokenType.INV):
                return self._parse_modified_gate_call()
            
            # Expression statements (assignments, function calls)
            else:
                return self._parse_expression_statement()
                
        except ParseError:
            # Skip to next statement on error
            self._synchronize()
            return None
    
    def _parse_const_declaration(self) -> VariableDeclaration:
        """Parse const variable declaration."""
        const_token = self._consume(TokenType.CONST, "Expected 'const'")
        
        # Parse type
        type_annotation = self._parse_type_annotation()
        
        # Parse name
        name = self._consume(TokenType.IDENTIFIER, "Expected variable name").value
        
        # Parse initializer (required for const)
        if not self._match(TokenType.ASSIGN):
            raise ParseError("Const declaration requires initialization", self._peek())
        
        initializer = self._parse_expression()
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after declaration")
        
        return VariableDeclaration(
            type_annotation=type_annotation,
            name=name,
            initializer=initializer,
            is_const=True,
            line=const_token.line,
            column=const_token.column
        )
    
    def _parse_variable_declaration(self) -> VariableDeclaration:
        """Parse variable declaration."""
        # Parse type
        type_token = self._peek()
        type_annotation = self._parse_type_annotation()
        
        # Check for array size immediately after type (e.g., "qubit[5]")
        if self._match(TokenType.LBRACKET):
            size = self._parse_expression()
            self._consume(TokenType.RBRACKET, "Expected ']' after array size")
            # Update the type annotation with the array size
            type_annotation = TypeAnnotation(
                base_type=type_annotation.base_type,
                size=size,
                line=type_annotation.line,
                column=type_annotation.column
            )
        
        # Parse name
        name = self._consume(TokenType.IDENTIFIER, "Expected variable name").value
        
        # Check for array size after variable name (e.g., "float arr[5]")
        if self._match(TokenType.LBRACKET):
            size = self._parse_expression()
            self._consume(TokenType.RBRACKET, "Expected ']' after array size")
            # Update the type annotation with the array size
            type_annotation = TypeAnnotation(
                base_type=type_annotation.base_type,
                size=size,
                line=type_annotation.line,
                column=type_annotation.column
            )
        
        # Parse optional initializer
        initializer = None
        if self._match(TokenType.ASSIGN):
            initializer = self._parse_expression()
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after declaration")
        
        return VariableDeclaration(
            type_annotation=type_annotation,
            name=name,
            initializer=initializer,
            is_const=False,
            line=type_token.line,
            column=type_token.column
        )
    
    def _parse_type_annotation(self) -> TypeAnnotation:
        """Parse type annotation."""
        type_token = self._advance()  # Consume type token
        base_type = type_token.value
        
        return TypeAnnotation(
            base_type=base_type,
            size=None,  # Array size is parsed separately in variable declarations
            line=type_token.line,
            column=type_token.column
        )
    
    def _parse_if_statement(self) -> IfStatement:
        """Parse if statement."""
        if_token = self._consume(TokenType.IF, "Expected 'if'")
        
        self._consume(TokenType.LPAREN, "Expected '(' after 'if'")
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after if condition")
        
        # Parse then body
        then_body = self._parse_block()
        
        # Parse optional else
        else_body = None
        if self._match(TokenType.ELSE):
            else_body = self._parse_block()
        
        return IfStatement(
            condition=condition,
            then_body=then_body,
            else_body=else_body,
            line=if_token.line,
            column=if_token.column
        )
    
    def _parse_for_statement(self) -> ForStatement:
        """Parse for statement."""
        for_token = self._consume(TokenType.FOR, "Expected 'for'")
        
        self._consume(TokenType.LPAREN, "Expected '(' after 'for'")
        
        # Parse variable type (optional in some contexts, but required in OpenQASM 3.0)
        if self._check(TokenType.INT) or self._check(TokenType.UINT) or self._check(TokenType.FLOAT_KW):
            # Skip type declaration, we'll infer it from the iterable
            self._advance()
        
        variable = self._consume(TokenType.IDENTIFIER, "Expected loop variable").value
        self._consume(TokenType.IN, "Expected 'in' after loop variable")
        iterable = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after for clause")
        
        body = self._parse_block()
        
        return ForStatement(
            variable=variable,
            iterable=iterable,
            body=body,
            line=for_token.line,
            column=for_token.column
        )
    
    def _parse_block(self) -> List[Statement]:
        """Parse a block of statements."""
        statements = []
        
        if self._match(TokenType.LBRACE):
            # Multi-statement block
            while not self._check(TokenType.RBRACE) and not self._is_at_end():
                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)
            
            self._consume(TokenType.RBRACE, "Expected '}' after block")
        else:
            # Single statement
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return statements
    
    def _parse_gate_definition(self) -> GateDefinition:
        """Parse gate definition."""
        gate_token = self._consume(TokenType.GATE, "Expected 'gate'")
        
        name = self._consume(TokenType.IDENTIFIER, "Expected gate name").value
        
        # Parse optional parameters
        parameters = []
        if self._match(TokenType.LPAREN):
            if not self._check(TokenType.RPAREN):
                # Check if we have a typed parameter (type followed by name)
                if self._check(TokenType.ANGLE) or self._check(TokenType.FLOAT_KW) or self._check(TokenType.INT) or self._check(TokenType.UINT) or self._check(TokenType.BOOL):
                    # This could be a typed parameter like "angle theta" or just "angle" as parameter name
                    type_token = self._advance()
                    
                    # Check if there's an identifier after the type (typed parameter)
                    if self._check(TokenType.IDENTIFIER):
                        # This is a typed parameter like "angle theta"
                        parameters.append(self._consume(TokenType.IDENTIFIER, "Expected parameter name").value)
                    else:
                        # This is just the type name used as parameter name like "angle"
                        parameters.append(type_token.value)
                    
                    # If we have more parameters, parse them
                    while self._match(TokenType.COMMA):
                        if self._check(TokenType.ANGLE) or self._check(TokenType.FLOAT_KW) or self._check(TokenType.INT) or self._check(TokenType.UINT) or self._check(TokenType.BOOL):
                            type_token = self._advance()
                            if self._check(TokenType.IDENTIFIER):
                                parameters.append(self._consume(TokenType.IDENTIFIER, "Expected parameter name").value)
                            else:
                                parameters.append(type_token.value)
                        else:
                            break
                else:
                    # This is an untyped parameter like "theta"
                    parameters.append(self._consume(TokenType.IDENTIFIER, "Expected parameter name").value)
                    while self._match(TokenType.COMMA):
                        parameters.append(self._consume(TokenType.IDENTIFIER, "Expected parameter name").value)
            self._consume(TokenType.RPAREN, "Expected ')' after parameters")
        
        # Parse qubit parameters
        qubits = []
        qubit = self._consume(TokenType.IDENTIFIER, "Expected qubit parameter").value
        qubits.append(qubit)
        while self._match(TokenType.COMMA):
            qubits.append(self._consume(TokenType.IDENTIFIER, "Expected qubit parameter").value)
        
        # Parse body
        body = self._parse_block()
        
        return GateDefinition(
            name=name,
            parameters=parameters,
            qubits=qubits,
            body=body,
            line=gate_token.line,
            column=gate_token.column
        )
    
    def _parse_modified_gate_call(self) -> GateCall:
        """Parse gate call with modifiers (ctrl@, inv@)."""
        modifiers = []
        
        # Parse modifiers
        while self._check(TokenType.CTRL) or self._check(TokenType.INV):
            modifier_token = self._advance()
            modifier_type = modifier_token.value
            
            # Check for @ symbol
            self._consume(TokenType.AT, f"Expected '@' after '{modifier_type}'")
            
            # Check for parameter (for ctrl@(n))
            parameter = None
            if modifier_type == 'ctrl' and self._match(TokenType.LPAREN):
                parameter = self._parse_expression()
                self._consume(TokenType.RPAREN, "Expected ')' after ctrl parameter")
            
            modifiers.append(GateModifier(
                type=modifier_type,
                parameter=parameter,
                line=modifier_token.line,
                column=modifier_token.column
            ))
        
        # Parse gate call
        gate_token = self._peek()
        name = self._consume(TokenType.IDENTIFIER, "Expected gate name").value
        
        # Parse optional parameters
        parameters = []
        if self._match(TokenType.LPAREN):
            if not self._check(TokenType.RPAREN):
                parameters.append(self._parse_expression())
                while self._match(TokenType.COMMA):
                    parameters.append(self._parse_expression())
            self._consume(TokenType.RPAREN, "Expected ')' after parameters")
        
        # Parse qubit arguments
        qubits = []
        qubit = self._parse_expression()
        qubits.append(qubit)
        while self._match(TokenType.COMMA):
            qubits.append(self._parse_expression())
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after gate call")
        
        return GateCall(
            name=name,
            parameters=parameters,
            qubits=qubits,
            modifiers=modifiers,
            line=gate_token.line,
            column=gate_token.column
        )
    
    def _parse_measurement(self) -> MeasurementStatement:
        """Parse measurement statement."""
        measure_token = self._consume(TokenType.MEASURE, "Expected 'measure'")
        
        qubit = self._parse_expression()
        
        # Optional target
        target = None
        if self._match(TokenType.ARROW):
            target = self._parse_expression()
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after measurement")
        
        return MeasurementStatement(
            qubit=qubit,
            target=target,
            line=measure_token.line,
            column=measure_token.column
        )
    
    def _parse_reset(self) -> ResetStatement:
        """Parse reset statement."""
        reset_token = self._consume(TokenType.RESET, "Expected 'reset'")
        
        qubit = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after reset")
        
        return ResetStatement(
            qubit=qubit,
            line=reset_token.line,
            column=reset_token.column
        )
    
    def _parse_barrier(self) -> BarrierStatement:
        """Parse barrier statement."""
        barrier_token = self._consume(TokenType.BARRIER, "Expected 'barrier'")
        
        qubits = []
        qubit = self._parse_expression()
        qubits.append(qubit)
        while self._match(TokenType.COMMA):
            qubits.append(self._parse_expression())
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after barrier")
        
        return BarrierStatement(
            qubits=qubits,
            line=barrier_token.line,
            column=barrier_token.column
        )
    
    def _parse_expression_statement(self) -> Statement:
        """Parse expression statement (assignment or function call)."""
        expr = self._parse_expression()
        
        # Check for assignment
        if self._match(TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN):
            operator = self._previous().value
            value = self._parse_expression()
            if not self._check(TokenType.SEMICOLON):
                raise ParseError("Expected ';' after assignment", self._peek())
            self._advance()  # consume semicolon
            
            return Assignment(
                target=expr,
                operator=operator,
                value=value,
                line=expr.line,
                column=expr.column
            )
        else:
            # Check if it's a gate call without modifiers
            if isinstance(expr, Identifier):
                # Look ahead to see if this is a gate call
                if not self._check(TokenType.SEMICOLON):
                    # Parse as gate call
                    name = expr.name
                    parameters = []
                    qubits = []

                    # Parse parameters if present
                    if self._match(TokenType.LPAREN):
                        if not self._check(TokenType.RPAREN):
                            parameters.append(self._parse_expression())
                            while self._match(TokenType.COMMA):
                                parameters.append(self._parse_expression())
                        self._consume(TokenType.RPAREN, "Expected ')' after parameters")

                    # Parse qubit arguments
                    if not self._check(TokenType.SEMICOLON):
                        qubit = self._parse_expression()
                        qubits.append(qubit)
                        while self._match(TokenType.COMMA):
                            qubits.append(self._parse_expression())

                    if not self._check(TokenType.SEMICOLON):
                        raise ParseError("Expected ';' after gate call", self._peek())
                    self._advance()  # consume semicolon

                    return GateCall(
                        name=name,
                        parameters=parameters,
                        qubits=qubits,
                        modifiers=[],
                        line=expr.line,
                        column=expr.column
                    )
            elif isinstance(expr, FunctionCall):
                # This is a function call that might be a gate call
                # Parse as gate call
                name = expr.name
                parameters = expr.arguments
                qubits = []

                # Parse qubit arguments
                if not self._check(TokenType.SEMICOLON):
                    qubit = self._parse_expression()
                    qubits.append(qubit)
                    while self._match(TokenType.COMMA):
                        qubits.append(self._parse_expression())

                if not self._check(TokenType.SEMICOLON):
                    raise ParseError("Expected ';' after gate call", self._peek())
                self._advance()  # consume semicolon

                return GateCall(
                    name=name,
                    parameters=parameters,
                    qubits=qubits,
                    modifiers=[],
                    line=expr.line,
                    column=expr.column
                )
            
            if not self._check(TokenType.SEMICOLON):
                raise ParseError("Expected ';' after expression", self._peek())
            self._advance()  # consume semicolon
            
            return ExpressionStatement(
                expression=expr,
                line=expr.line,
                column=expr.column
            )
    
    def _parse_expression(self) -> Expression:
        """Parse expression."""
        return self._parse_logical_or()
    
    def _parse_logical_or(self) -> Expression:
        """Parse logical OR expression."""
        expr = self._parse_logical_and()
        
        while self._match(TokenType.OR):
            operator = self._previous().value
            right = self._parse_logical_and()
            expr = BinaryOperation(
                left=expr,
                operator=operator,
                right=right,
                line=expr.line,
                column=expr.column
            )
        
        return expr
    
    def _parse_logical_and(self) -> Expression:
        """Parse logical AND expression."""
        expr = self._parse_equality()
        
        while self._match(TokenType.AND):
            operator = self._previous().value
            right = self._parse_equality()
            expr = BinaryOperation(
                left=expr,
                operator=operator,
                right=right,
                line=expr.line,
                column=expr.column
            )
        
        return expr
    
    def _parse_equality(self) -> Expression:
        """Parse equality expression."""
        expr = self._parse_comparison()
        
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self._previous().value
            right = self._parse_comparison()
            expr = BinaryOperation(
                left=expr,
                operator=operator,
                right=right,
                line=expr.line,
                column=expr.column
            )
        
        return expr
    
    def _parse_comparison(self) -> Expression:
        """Parse comparison expression."""
        expr = self._parse_term()
        
        while self._match(TokenType.GREATER_THAN, TokenType.GREATER_EQUAL,
                          TokenType.LESS_THAN, TokenType.LESS_EQUAL):
            operator = self._previous().value
            right = self._parse_term()
            expr = BinaryOperation(
                left=expr,
                operator=operator,
                right=right,
                line=expr.line,
                column=expr.column
            )
        
        return expr
    
    def _parse_term(self) -> Expression:
        """Parse addition/subtraction expression."""
        expr = self._parse_factor()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous().value
            right = self._parse_factor()
            expr = BinaryOperation(
                left=expr,
                operator=operator,
                right=right,
                line=expr.line,
                column=expr.column
            )
        
        return expr
    
    def _parse_factor(self) -> Expression:
        """Parse multiplication/division expression."""
        expr = self._parse_power()
        
        while self._match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self._previous().value
            right = self._parse_power()
            expr = BinaryOperation(
                left=expr,
                operator=operator,
                right=right,
                line=expr.line,
                column=expr.column
            )
        
        return expr
    
    def _parse_power(self) -> Expression:
        """Parse power expression."""
        expr = self._parse_unary()
        
        if self._match(TokenType.POWER):
            operator = self._previous().value
            right = self._parse_power()  # Right associative
            expr = BinaryOperation(
                left=expr,
                operator=operator,
                right=right,
                line=expr.line,
                column=expr.column
            )
        
        return expr
    
    def _parse_unary(self) -> Expression:
        """Parse unary expression."""
        if self._match(TokenType.NOT, TokenType.MINUS, TokenType.PLUS):
            operator = self._previous().value
            right = self._parse_unary()
            return UnaryOperation(
                operator=operator,
                operand=right,
                line=self._previous().line,
                column=self._previous().column
            )
        
        return self._parse_postfix()
    
    def _parse_postfix(self) -> Expression:
        """Parse postfix expression (array access, function calls)."""
        expr = self._parse_primary()
        
        while True:
            if self._match(TokenType.LBRACKET):
                # Array access or slice
                if self._check(TokenType.COLON):
                    # Slice with no start
                    self._advance()  # consume ':'
                    end = None
                    if not self._check(TokenType.RBRACKET):
                        end = self._parse_expression()
                    self._consume(TokenType.RBRACKET, "Expected ']' after array slice")
                    expr = ArraySlice(
                        array=expr,
                        start=None,
                        end=end,
                        line=expr.line,
                        column=expr.column
                    )
                else:
                    index_or_start = self._parse_expression()
                    if self._match(TokenType.COLON):
                        # Slice
                        end = None
                        if not self._check(TokenType.RBRACKET):
                            end = self._parse_expression()
                        self._consume(TokenType.RBRACKET, "Expected ']' after array slice")
                        expr = ArraySlice(
                            array=expr,
                            start=index_or_start,
                            end=end,
                            line=expr.line,
                            column=expr.column
                        )
                    else:
                        # Simple access
                        self._consume(TokenType.RBRACKET, "Expected ']' after array index")
                        expr = ArrayAccess(
                            array=expr,
                            index=index_or_start,
                            line=expr.line,
                            column=expr.column
                        )
            elif self._match(TokenType.LPAREN):
                # Function call
                arguments = []
                if not self._check(TokenType.RPAREN):
                    arguments.append(self._parse_expression())
                    while self._match(TokenType.COMMA):
                        arguments.append(self._parse_expression())
                
                self._consume(TokenType.RPAREN, "Expected ')' after arguments")
                
                if isinstance(expr, Identifier):
                    expr = FunctionCall(
                        name=expr.name,
                        arguments=arguments,
                        line=expr.line,
                        column=expr.column
                    )
            else:
                break
        
        return expr
    
    def _parse_primary(self) -> Expression:
        """Parse primary expression."""
        # Literals
        if self._match(TokenType.BOOLEAN):
            value = self._previous().value == 'true'
            return Literal(
                value=value,
                type_name='bool',
                line=self._previous().line,
                column=self._previous().column
            )
        
        if self._match(TokenType.INTEGER):
            value = int(self._previous().value)
            return Literal(
                value=value,
                type_name='int',
                line=self._previous().line,
                column=self._previous().column
            )
        
        if self._match(TokenType.FLOAT):
            value = float(self._previous().value)
            return Literal(
                value=value,
                type_name='float',
                line=self._previous().line,
                column=self._previous().column
            )
        
        if self._match(TokenType.STRING):
            value = self._previous().value.strip('"\'')
            return Literal(
                value=value,
                type_name='string',
                line=self._previous().line,
                column=self._previous().column
            )
        
        # Range function
        if self._check(TokenType.RANGE) or (self._check(TokenType.IDENTIFIER) and self._peek().value == 'range'):
            range_token = self._advance()
            self._consume(TokenType.LPAREN, "Expected '(' after 'range'")
            
            # Parse range arguments
            args = []
            if not self._check(TokenType.RPAREN):
                args.append(self._parse_expression())
                while self._match(TokenType.COMMA):
                    args.append(self._parse_expression())
            
            self._consume(TokenType.RPAREN, "Expected ')' after range arguments")
            
            # Convert to RangeExpression
            if len(args) == 1:
                # range(stop)
                return RangeExpression(
                    start=None,
                    stop=args[0],
                    step=None,
                    line=range_token.line,
                    column=range_token.column
                )
            elif len(args) == 2:
                # range(start, stop)
                return RangeExpression(
                    start=args[0],
                    stop=args[1],
                    step=None,
                    line=range_token.line,
                    column=range_token.column
                )
            elif len(args) == 3:
                # range(start, stop, step)
                return RangeExpression(
                    start=args[0],
                    stop=args[1],
                    step=args[2],
                    line=range_token.line,
                    column=range_token.column
                )
            else:
                raise ParseError("Invalid number of arguments for range", range_token)
        
        # Identifiers
        if self._match(TokenType.IDENTIFIER):
            identifier_token = self._previous()
            identifier_name = identifier_token.value
            
            # Check for reserved keywords used as identifiers
            reserved_keywords = {
                'if', 'else', 'for', 'in', 'range', 'gate', 'measure', 'reset', 'barrier',
                'ctrl', 'inv', 'pow', 'const', 'OPENQASM', 'include'
            }
            
            if identifier_name in reserved_keywords:
                raise ParseError(f"Reserved keyword '{identifier_name}' cannot be used as identifier", identifier_token)
            
            return Identifier(
                name=identifier_name,
                line=identifier_token.line,
                column=identifier_token.column
            )
        
        # Parenthesized expressions
        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        # Error
        raise ParseError("Expected expression", self._peek())
    
    def _synchronize(self):
        """Synchronize parser after error by finding next statement."""
        self._advance()
        
        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
            
            if self._peek().type in [TokenType.IF, TokenType.FOR, TokenType.GATE,
                                   TokenType.MEASURE, TokenType.RESET, TokenType.BARRIER,
                                   TokenType.QUBIT, TokenType.BIT, TokenType.INT,
                                   TokenType.UINT, TokenType.FLOAT_KW, TokenType.ANGLE,
                                   TokenType.BOOL, TokenType.CONST]:
                return
            
            self._advance()


def test_parser():
    """Test the OpenQASM 3.0 parser with various inputs."""
    parser = QASMParser()
    printer = ASTPrinter()
    
    test_cases = [
        # Basic program
        '''OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;''',
        
        # Gate definition
        '''OPENQASM 3.0;
gate h q { }
gate cx a, b { }''',
        
        # Control flow
        '''OPENQASM 3.0;
int x = 5;
if (x > 0) {
    x = x + 1;
}''',
        
        # For loop
        '''OPENQASM 3.0;
qubit[5] q;
for (int i in range(5)) {
    h q[i];
}''',
        
        # Gate modifiers
        '''OPENQASM 3.0;
qubit[3] q;
ctrl @ x q[0], q[1];
inv @ h q[2];'''
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Parser Test Case {i+1} ---")
        print(f"Input:\n{test_case}")
        
        try:
            ast = parser.parse(test_case)
            print(f"\nAST:\n{printer.print_ast(ast)}")
        except ParseError as e:
            print(f"\nParse Error: {e}")

if __name__ == "__main__":
    test_parser()
