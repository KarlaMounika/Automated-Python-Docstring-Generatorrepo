# backend/code_inserter.py


import ast
from typing import List, Dict


def insert_docstrings_into_code(original_code: str,
                                parsed_data: Dict,
                                docstrings: List[Dict]) -> str:
    """
    Insert generated docstrings into the original Python code.

    Args:
        original_code (str): The original Python source code.
        parsed_data (Dict): Parsed metadata (not used here but kept for workflow compatibility).
        docstrings (List[Dict]): List of dictionaries containing:
                                 {
                                     "function_name": str,
                                     "docstring": str
                                 }

    Returns:
        str: Modified Python code with inserted docstrings.
    """

    # Parse original code into AST
    tree = ast.parse(original_code)

    # Create mapping: function_name -> docstring
    docstring_map = {
        item["function_name"]: item["docstring"]
        for item in docstrings
    }

    # NodeTransformer to insert docstrings
    class DocstringInserter(ast.NodeTransformer):

        def visit_FunctionDef(self, node):
            # Visit child nodes first
            self.generic_visit(node)

            if node.name in docstring_map:

                # Check if docstring already exists
                if (len(node.body) > 0 and
                        isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant) and
                        isinstance(node.body[0].value.value, str)):
                    # Replace existing docstring
                    node.body[0].value = ast.Constant(
                        value=docstring_map[node.name]
                    )
                else:
                    # Insert new docstring at top
                    docstring_node = ast.Expr(
                        value=ast.Constant(
                            value=docstring_map[node.name]
                        )
                    )
                    node.body.insert(0, docstring_node)

            return node

    # Apply transformation
    transformer = DocstringInserter()
    modified_tree = transformer.visit(tree)

    # Fix missing locations
    ast.fix_missing_locations(modified_tree)

    # Convert AST back to source code
    modified_code = ast.unparse(modified_tree)

    return modified_code


# Example usage (for testing)
if __name__ == "__main__":

    original_code = '''
def add(a, b):
    return a + b

def greet(name):
    print("Hello", name)
'''

    docstrings = [
        {
            "function_name": "add",
            "docstring": "Add two numbers and return the result."
        },
        {
            "function_name": "greet",
            "docstring": "Print greeting message to the user."
        }
    ]

    result = insert_docstrings_into_code(
        original_code,
        parsed_data={},
        docstrings=docstrings
    )

    print("Modified Code:\n")
    print(result)