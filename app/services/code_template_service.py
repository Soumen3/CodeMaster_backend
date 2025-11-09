"""
Code template generation service for different programming languages.
Generates dynamic code snippets based on problem specifications.
"""
import json
from typing import Dict, Optional


def generate_python_template(
    function_name: str,
    parameters: Dict[str, str],
    return_type: Optional[str] = None
) -> str:
    """
    Generate Python code template.
    
    Args:
        function_name: Name of the solution function
        parameters: Dictionary of parameter_name: type (e.g., {"nums": "list[int]", "target": "int"})
        return_type: Expected return type (optional)
    
    Returns:
        Python code template string
    """
    # Build function signature
    param_str = ", ".join(parameters.keys())
    
    # Build input parsing
    input_lines = []
    for param_name, param_type in parameters.items():
        if param_type in ["list", "array", "list[int]", "list<int>"]:
            input_lines.append(f"    {param_name} = [int(e) for e in input().split()]")
        elif param_type == "int":
            input_lines.append(f"    {param_name} = int(input())")
        elif param_type == "float":
            input_lines.append(f"    {param_name} = float(input())")
        elif param_type in ["str", "string"]:
            input_lines.append(f"    {param_name} = input()")
        else:
            # Default to string input
            input_lines.append(f"    {param_name} = input()")
    
    input_parsing = "\n".join(input_lines)
    
    template = f"""def {function_name}({param_str}):
    # Write your code here
    pass

if __name__ == "__main__":
{input_parsing}
    result = {function_name}({param_str})
    print(result)"""
    
    return template


def generate_javascript_template(
    function_name: str,
    parameters: Dict[str, str],
    return_type: Optional[str] = None
) -> str:
    """Generate JavaScript code template."""
    param_str = ", ".join(parameters.keys())
    
    # Build input parsing
    input_lines = []
    for i, (param_name, param_type) in enumerate(parameters.items()):
        if param_type in ["list", "array", "list[int]", "list<int>"]:
            input_lines.append(f"    const {param_name} = lines[{i}].split(' ').map(Number);")
        elif param_type == "int":
            input_lines.append(f"    const {param_name} = parseInt(lines[{i}]);")
        elif param_type == "float":
            input_lines.append(f"    const {param_name} = parseFloat(lines[{i}]);")
        else:
            input_lines.append(f"    const {param_name} = lines[{i}];")
    
    input_parsing = "\n".join(input_lines)
    
    template = f"""function {function_name}({param_str}) {{
    // Write your code here
    
}}

const readline = require('readline');
const rl = readline.createInterface({{
    input: process.stdin,
    output: process.stdout
}});

const lines = [];
rl.on('line', (line) => {{
    lines.push(line);
}});

rl.on('close', () => {{
{input_parsing}
    const result = {function_name}({param_str});
    console.log(result);
}});"""
    
    return template


def generate_cpp_template(
    function_name: str,
    parameters: Dict[str, str],
    return_type: Optional[str] = None
) -> str:
    """Generate C++ code template."""
    # Map types
    type_map = {
        "int": "int",
        "float": "double",
        "str": "string",
        "string": "string",
        "list": "vector<int>",
        "array": "vector<int>",
        "list[int]": "vector<int>",
        "list<int>": "vector<int>"
    }
    
    # Build function signature
    cpp_return_type = type_map.get(return_type, "auto")
    param_list = []
    for param_name, param_type in parameters.items():
        cpp_type = type_map.get(param_type, "string")
        if "vector" in cpp_type or "string" in cpp_type:
            param_list.append(f"{cpp_type}& {param_name}")
        else:
            param_list.append(f"{cpp_type} {param_name}")
    
    param_str = ", ".join(param_list)
    
    # Build input parsing
    input_lines = []
    for param_name, param_type in parameters.items():
        if param_type in ["list", "array", "list[int]", "list<int>"]:
            input_lines.append(f"""    vector<int> {param_name};
    int temp;
    while (cin >> temp) {{
        {param_name}.push_back(temp);
        if (cin.peek() == '\\n') break;
    }}""")
        elif param_type == "int":
            input_lines.append(f"    int {param_name};")
            input_lines.append(f"    cin >> {param_name};")
        elif param_type == "float":
            input_lines.append(f"    double {param_name};")
            input_lines.append(f"    cin >> {param_name};")
        else:
            input_lines.append(f"    string {param_name};")
            input_lines.append(f"    getline(cin, {param_name});")
    
    input_parsing = "\n".join(input_lines)
    call_args = ", ".join(parameters.keys())
    
    # Build output statement based on return type
    if cpp_return_type == "vector<int>":
        output_lines = """    auto result = {function_name}({call_args});
    cout << "[";
    for (int i = 0; i < result.size(); i++) {{
        cout << result[i];
        if (i < result.size() - 1) cout << ", ";
    }}
    cout << "]" << endl;"""
    else:
        output_lines = """    auto result = {function_name}({call_args});
    cout << result << endl;"""
    
    output_lines = output_lines.format(function_name=function_name, call_args=call_args)
    
    template = f"""#include <iostream>
#include <vector>
#include <string>
using namespace std;

{cpp_return_type} {function_name}({param_str}) {{
    // Write your code here
    
}}

int main() {{
{input_parsing}
{output_lines}
    return 0;
}}"""
    
    return template


def generate_java_template(
    function_name: str,
    parameters: Dict[str, str],
    return_type: Optional[str] = None
) -> str:
    """Generate Java code template."""
    # Map types
    type_map = {
        "int": "int",
        "float": "double",
        "str": "String",
        "string": "String",
        "list": "int[]",
        "array": "int[]",
        "list[int]": "int[]",
        "list<int>": "int[]"
    }
    
    # Build function signature
    java_return_type = type_map.get(return_type, "Object")
    param_list = []
    for param_name, param_type in parameters.items():
        java_type = type_map.get(param_type, "String")
        param_list.append(f"{java_type} {param_name}")
    
    param_str = ", ".join(param_list)
    
    # Build input parsing
    input_lines = []
    for param_name, param_type in parameters.items():
        if param_type in ["list", "array", "list[int]", "list<int>"]:
            input_lines.append(f"""        String[] tokens = scanner.nextLine().split(" ");
        int[] {param_name} = new int[tokens.length];
        for (int i = 0; i < tokens.length; i++) {{
            {param_name}[i] = Integer.parseInt(tokens[i]);
        }}""")
        elif param_type == "int":
            input_lines.append(f"        int {param_name} = scanner.nextInt();")
        elif param_type == "float":
            input_lines.append(f"        double {param_name} = scanner.nextDouble();")
        else:
            input_lines.append(f"        String {param_name} = scanner.nextLine();")
    
    input_parsing = "\n".join(input_lines)
    call_args = ", ".join(parameters.keys())
    
    # Build output statement based on return type
    if java_return_type == "int[]":
        output_lines = f"""        {java_return_type} result = {function_name}({call_args});
        System.out.print("[");
        for (int i = 0; i < result.length; i++) {{
            System.out.print(result[i]);
            if (i < result.length - 1) System.out.print(", ");
        }}
        System.out.println("]");"""
    else:
        output_lines = f"""        {java_return_type} result = {function_name}({call_args});
        System.out.println(result);"""
    
    template = f"""import java.util.*;

public class Solution {{
    public static {java_return_type} {function_name}({param_str}) {{
        // Write your code here
        return null;
    }}
    
    public static void main(String[] args) {{
        Scanner scanner = new Scanner(System.in);
{input_parsing}
{output_lines}
        scanner.close();
    }}
}}"""
    
    return template


def generate_c_template(
    function_name: str,
    parameters: Dict[str, str],
    return_type: Optional[str] = None
) -> str:
    """Generate C code template."""
    # Map return type
    type_map = {
        "int": "int",
        "float": "double",
        "str": "char*",
        "string": "char*",
        "list": "int*",
        "array": "int*",
        "list[int]": "int*",
        "list<int>": "int*",
        "bool": "int"
    }
    
    c_return_type = type_map.get(return_type, "int") if return_type else "int"
    
    # Build function signature
    param_list = []
    for param_name, param_type in parameters.items():
        if param_type in ["list", "array", "list[int]", "list<int>"]:
            param_list.append(f"int {param_name}[]")
            param_list.append(f"int {param_name}_size")
        elif param_type == "int":
            param_list.append(f"int {param_name}")
        elif param_type == "float":
            param_list.append(f"double {param_name}")
        elif param_type in ["str", "string"]:
            param_list.append(f"char {param_name}[]")
        else:
            param_list.append(f"int {param_name}")
    
    param_str = ", ".join(param_list)
    
    # Build input parsing and function call
    input_lines = []
    call_args = []
    
    for param_name, param_type in parameters.items():
        if param_type in ["list", "array", "list[int]", "list<int>"]:
            input_lines.append(f"""    // Read array {param_name}
    char line[10000];
    fgets(line, sizeof(line), stdin);
    int {param_name}[1000];
    int {param_name}_size = 0;
    char *token = strtok(line, " \\n");
    while (token != NULL) {{
        {param_name}[{param_name}_size++] = atoi(token);
        token = strtok(NULL, " \\n");
    }}""")
            call_args.append(param_name)
            call_args.append(f"{param_name}_size")
        elif param_type == "int":
            input_lines.append(f"""    int {param_name};
    scanf("%d", &{param_name});""")
            call_args.append(param_name)
        elif param_type == "float":
            input_lines.append(f"""    double {param_name};
    scanf("%lf", &{param_name});""")
            call_args.append(param_name)
        elif param_type in ["str", "string"]:
            input_lines.append(f"""    char {param_name}[1000];
    scanf("%s", {param_name});""")
            call_args.append(param_name)
        else:
            input_lines.append(f"""    int {param_name};
    scanf("%d", &{param_name});""")
            call_args.append(param_name)
    
    input_parsing = "\n".join(input_lines)
    call_args_str = ", ".join(call_args)
    
    # Build output statement based on return type
    if c_return_type == "int":
        output_line = "    printf(\"%d\\n\", result);"
    elif c_return_type == "double":
        output_line = "    printf(\"%lf\\n\", result);"
    elif c_return_type == "char*":
        output_line = "    printf(\"%s\\n\", result);"
    elif c_return_type == "int*":
        # For array returns, we need to know the size
        # Common pattern: Two Sum returns array of size 2
        output_line = """    // Print array result (assuming size 2 for Two Sum)
    // Modify the loop size based on your problem's return array size
    printf("[");
    for (int i = 0; i < 2; i++) {
        printf("%d", result[i]);
        if (i < 1) printf(", ");
    }
    printf("]\\n");"""
    else:
        output_line = "    printf(\"%d\\n\", result);"
    
    template = f"""#include <stdio.h>
#include <stdlib.h>
#include <string.h>

{c_return_type} {function_name}({param_str}) {{
    // Write your code here
    
}}

int main() {{
{input_parsing}
    
    {c_return_type} result = {function_name}({call_args_str});
{output_line}
    
    return 0;
}}"""
    
    return template


def get_code_template(
    language: str,
    function_name: str = "solution",
    parameters: Optional[Dict[str, str]] = None,
    return_type: Optional[str] = None
) -> str:
    """
    Get code template for specified language and problem parameters.
    
    Args:
        language: Programming language (python, javascript, cpp, java, c)
        function_name: Name of the solution function
        parameters: Dictionary of parameter_name: type (e.g., {"nums": "list[int]", "target": "int"})
        return_type: Expected return type
    
    Returns:
        Code template string
    
    Example:
        parameters = {"nums": "list[int]", "target": "int"}
        template = get_code_template("python", "twoSum", parameters, "list")
    """
    if parameters is None:
        parameters = {}
    
    generators = {
        "python": generate_python_template,
        "javascript": generate_javascript_template,
        "cpp": generate_cpp_template,
        "java": generate_java_template,
        "c": generate_c_template
    }
    
    generator = generators.get(language.lower())
    if not generator:
        raise ValueError(f"Unsupported language: {language}")
    
    return generator(function_name, parameters, return_type)


def parse_parameters_from_json(parameters_json: Optional[str]) -> Dict[str, str]:
    """
    Parse parameters from JSON string stored in database.
    
    Args:
        parameters_json: JSON string like '{"nums": "list[int]", "target": "int"}'
    
    Returns:
        Dictionary of parameter_name: type
    """
    if not parameters_json:
        return {}
    
    try:
        return json.loads(parameters_json)
    except json.JSONDecodeError:
        return {}
