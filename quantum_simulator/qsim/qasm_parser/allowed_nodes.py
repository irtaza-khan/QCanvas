# qsim/qasm_parser/allowed_nodes.py

# Central place for controlling which AST node types QSim supports
ALLOWED_NODE_TYPES = {
    "Include",
    "QubitDeclaration",
    "ClassicalDeclaration",
    "GateDeclaration",
    "GateCall",
    "Barrier",
    "ConstantDeclaration",
    "Measurement",
    "QuantumMeasurementStatement",
    "Reset",
    "IfStatement",
    "ForLoop",        # can be unrolled if needed
    "ClassicalAssignment",
    "QuantumGateDefinition",
    "QuantumGate",#Gatecall
    "QuantumBarrier",#Barrier
    "QuantumMeasurementStatement",#Measure
    "QuantumMeasurementAssignment",
    "QuantumReset",#Reset
    "ClassicalDeclaration",
    "BranchingStatement",#If
    "ForInLoop",        # can be unrolled if needed
    "ClassicalAssignment",
    "ExpressionStatement",
    "BinaryExpression",
    "UnaryExpression",
    "QuantumReset",
    "ConstantDeclaration",
    "ClassicalAssignment",
    "AliasStatement",
    "Concatenation",
    "BranchingStatement",
    "ForInLoop",
    "QuantumBarrier",
    "QuantumGateDefinition",
    "QuantumPhase",
    "Include",
    "IndexedIdentifier",
    "QuantumBarrier",
    "ArrayDeclaration",
    "IntegerLiteral",
    "AliasStatement",
    "QuantumGateModifier",
    "ForLoop",
    "IODeclaration",   # input / output directives

}
