"""
OpenQASM 3.0 Compiler Package

A complete OpenQASM 3.0 Iteration I compiler implementation including:
- Lexical analysis (tokenization)
- Syntax analysis (parsing)
- Semantic analysis (type checking)
- Code generation (AST to source)

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

from .lexer import QASMLexer, Token, TokenType
from .parser import QASMParser, ParseError
from .ast_nodes import *
from .type_system import SemanticAnalyzer, SemanticError, TypeInfo, QASMType
from .codegen import CodeGenerator, PrettyPrinter

# Main compiler interface
class OpenQASM3Compiler:
    """Complete OpenQASM 3.0 compiler interface."""
    
    def __init__(self):
        self.lexer = QASMLexer()
        self.parser = QASMParser()
        self.analyzer = SemanticAnalyzer()
        self.generator = CodeGenerator()
        self.pretty_printer = PrettyPrinter()
    
    def compile(self, source: str, validate: bool = True) -> dict:
        """
        Compile OpenQASM 3.0 source code.
        
        Args:
            source: OpenQASM 3.0 source code
            validate: Whether to perform semantic validation
            
        Returns:
            Dictionary containing compilation results
        """
        result = {
            "success": False,
            "ast": None,
            "tokens": None,
            "errors": [],
            "warnings": [],
            "generated_code": None
        }
        
        try:
            # Tokenize
            tokens = self.lexer.tokenize(source)
            result["tokens"] = tokens
            
            # Parse
            ast = self.parser.parse(source)
            result["ast"] = ast
            
            # Semantic analysis
            if validate:
                semantic_success = self.analyzer.analyze(ast)
                if not semantic_success:
                    result["errors"] = [str(e) for e in self.analyzer.get_errors()]
                    result["warnings"] = self.analyzer.get_warnings()
                    return result
                
                result["warnings"] = self.analyzer.get_warnings()
            
            # Code generation (for validation)
            generated = self.generator.generate(ast)
            result["generated_code"] = generated
            
            result["success"] = True
            
        except ParseError as e:
            result["errors"] = [str(e)]
        except Exception as e:
            result["errors"] = [f"Compilation failed: {str(e)}"]
        
        return result
    
    def validate(self, source: str) -> dict:
        """
        Validate OpenQASM 3.0 source code without code generation.
        
        Args:
            source: OpenQASM 3.0 source code
            
        Returns:
            Dictionary containing validation results
        """
        result = self.compile(source, validate=True)
        # Remove generated code from validation result
        if "generated_code" in result:
            del result["generated_code"]
        return result
    
    def format(self, source: str, pretty: bool = True) -> str:
        """
        Format OpenQASM 3.0 source code.
        
        Args:
            source: OpenQASM 3.0 source code
            pretty: Whether to use pretty printing
            
        Returns:
            Formatted source code
            
        Raises:
            ParseError: If source code is invalid
        """
        ast = self.parser.parse(source)
        
        if pretty:
            return self.pretty_printer.generate(ast)
        else:
            return self.generator.generate(ast)
    
    def get_ast(self, source: str) -> Program:
        """
        Parse source code and return AST.
        
        Args:
            source: OpenQASM 3.0 source code
            
        Returns:
            Program AST node
        """
        return self.parser.parse(source)
    
    def get_tokens(self, source: str) -> List[Token]:
        """
        Tokenize source code.
        
        Args:
            source: OpenQASM 3.0 source code
            
        Returns:
            List of tokens
        """
        return self.lexer.tokenize(source)

# Convenience functions
def compile_qasm3(source: str, validate: bool = True) -> dict:
    """Compile OpenQASM 3.0 source code."""
    compiler = OpenQASM3Compiler()
    return compiler.compile(source, validate)

def validate_qasm3(source: str) -> dict:
    """Validate OpenQASM 3.0 source code."""
    compiler = OpenQASM3Compiler()
    return compiler.validate(source)

def format_qasm3(source: str, pretty: bool = True) -> str:
    """Format OpenQASM 3.0 source code."""
    compiler = OpenQASM3Compiler()
    return compiler.format(source, pretty)

def parse_qasm3(source: str) -> Program:
    """Parse OpenQASM 3.0 source code and return AST."""
    compiler = OpenQASM3Compiler()
    return compiler.get_ast(source)

__all__ = [
    # Main compiler
    'OpenQASM3Compiler',
    
    # Convenience functions
    'compile_qasm3',
    'validate_qasm3', 
    'format_qasm3',
    'parse_qasm3',
    
    # Core components
    'QASMLexer',
    'QASMParser', 
    'SemanticAnalyzer',
    'CodeGenerator',
    'PrettyPrinter',
    
    # AST nodes
    'Program',
    'Statement',
    'Expression',
    'VariableDeclaration',
    'Assignment',
    'IfStatement',
    'ForStatement',
    'GateDefinition',
    'GateCall',
    'MeasurementStatement',
    'ResetStatement',
    'BarrierStatement',
    'Literal',
    'Identifier',
    'BinaryOperation',
    'UnaryOperation',
    'ArrayAccess',
    'ArraySlice',
    'FunctionCall',
    'TypeAnnotation',
    'RangeExpression',
    'GateModifier',
    
    # Types and errors
    'TypeInfo',
    'QASMType',
    'ParseError',
    'SemanticError',
    'Token',
    'TokenType',
]
