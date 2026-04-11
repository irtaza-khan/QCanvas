import ast
from quantum_converters.parsers.cirq_parser import CirqASTVisitor

def test_cirq_expression_resolved():
    v = CirqASTVisitor()
    v.variables['layer'] = 0
    v.variables['i'] = 1
    
    # Simulate weights[layer, i, 0]
    node = ast.Subscript(
        value=ast.Name(id='weights', ctx=ast.Load()),
        slice=ast.Tuple(
            elts=[
                ast.Name(id='layer', ctx=ast.Load()),
                ast.Name(id='i', ctx=ast.Load()),
                ast.Constant(value=0)
            ],
            ctx=ast.Load()
        ),
        ctx=ast.Load()
    )
    
    result = v._extract_expression(node)
    print(f"Extracted expression: {result}")
    print(f"Array Parameters tracked: {v.array_parameters}")
    
    if result == "weights[0, 1, 0]" and v.array_parameters.get('weights') == [1, 2, 1]:
        # weights[0, 1, 0] -> indices 0, 1, 0 -> sizes max(0+1, 1+1, 0+1) -> [1, 2, 1]
        print("SUCCESS: Cirq expression resolution verified!")
    else:
        print("FAILURE: Cirq expression resolution failed.")

if __name__ == "__main__":
    test_cirq_expression_resolved()
