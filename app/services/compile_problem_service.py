import subprocess
import json
import tempfile
import os
import time
from sqlalchemy.orm import Session
from ..database.models import Problem, TestCase
from ..database.schemas import CompileProblemRequest, TestCaseResult
from icecream import ic


ic.disable()


def normalize_output(output: str) -> str:
    """
    Normalize output for comparison.
    Handles JSON arrays/objects and various output formats from different languages.
    
    Args:
        output: The output string to normalize
        
    Returns:
        Normalized output string
    """
    output = output.strip()
    
    # Try to parse as JSON and normalize
    try:
        parsed = json.loads(output)
        # Re-serialize without spaces for consistent comparison
        return json.dumps(parsed, separators=(',', ':'), sort_keys=True)
    except (json.JSONDecodeError, TypeError):
        pass
    
    # Try to convert common C/C++/Java output formats to JSON format
    # Handle formats like: "1, 2," or "0, 1," or "1 2" (space-separated)
    if output:
        # Remove trailing commas and spaces
        cleaned = output.rstrip(', \n\r\t')
        
        # Try to detect if it's array-like output without brackets
        # Check if it contains numbers/values separated by commas or spaces
        if ',' in cleaned or ' ' in cleaned:
            # Try to convert "1, 2" or "1 2" to "[1,2]"
            try:
                # Split by comma or space
                parts = [p.strip() for p in cleaned.replace(',', ' ').split() if p.strip()]
                
                # Try to parse each part as a number or keep as string
                parsed_parts = []
                for part in parts:
                    try:
                        # Try int first
                        parsed_parts.append(int(part))
                    except ValueError:
                        try:
                            # Try float
                            parsed_parts.append(float(part))
                        except ValueError:
                            # Keep as string, remove quotes if present
                            parsed_parts.append(part.strip('"\''))
                
                # If we successfully parsed some parts, convert to JSON array
                if parsed_parts:
                    return json.dumps(parsed_parts, separators=(',', ':'))
            except Exception:
                pass
    
    # If all parsing fails, just return stripped output
    return output


def compare_outputs(actual: str, expected: str) -> bool:
    """
    Compare actual and expected outputs with normalization.
    
    Args:
        actual: Actual output from code execution
        expected: Expected output from test case
        
    Returns:
        True if outputs match, False otherwise
    """
    return normalize_output(actual) == normalize_output(expected)


def compile_problem_code(compile_request: CompileProblemRequest, db: Session) -> dict:
    """
    Compile and run code against test cases for a given problem.
    
    Args:
        compile_request: Contains problem_id, code, and language
        db: Database session
        
    Returns:
        Dictionary with execution results
    """
    # Fetch the problem
    problem = db.query(Problem).filter(Problem.id == compile_request.problem_id).first()
    if not problem:
        raise ValueError(f"Problem with id {compile_request.problem_id} not found")
    
    # Fetch test cases (only public ones for "Run Code")
    test_cases = db.query(TestCase).filter(
        TestCase.problem_id == compile_request.problem_id,
        TestCase.is_hidden == False
    ).all()
    
    if not test_cases:
        return {
            "success": False,
            "message": "No test cases found for this problem",
            "test_results": [],
            "total_tests": 0,
            "passed_tests": 0,
            "execution_time": 0.0
        }
    
    # Execute code against test cases
    test_results = []
    passed_count = 0
    total_execution_time = 0.0
    
    for test_case in test_cases:
        result = execute_code(
            compile_request.code,
            compile_request.language,
            test_case.input_data,
            test_case.expected_output
        )
        test_results.append(result)
        if result["passed"]:
            passed_count += 1
        if result["execution_time"]:
            total_execution_time += result["execution_time"]
    
    success = passed_count == len(test_cases)
    
    return {
        "success": success,
        "message": f"Passed {passed_count}/{len(test_cases)} test cases" if success else f"Failed {len(test_cases) - passed_count} test case(s)",
        "test_results": test_results,
        "total_tests": len(test_cases),
        "passed_tests": passed_count,
        "execution_time": total_execution_time
    }


def execute_code(code: str, language: str, input_data: str, expected_output: str) -> dict:
    """
    Execute code with given input and compare with expected output.
    
    Args:
        code: Source code to execute
        language: Programming language
        input_data: Input for the code (can be JSON or plain text)
        expected_output: Expected output
        
    Returns:
        TestCaseResult dictionary
    """
    start_time = time.time()
    
    try:
        # Convert JSON input to line-by-line format for stdin
        input_str = convert_input_format(input_data)
        
        # Execute based on language
        if language == "python":
            actual_output, error = execute_python(code, input_str)
        elif language == "javascript":
            actual_output, error = execute_javascript(code, input_str)
        elif language == "cpp":
            actual_output, error = execute_cpp(code, input_str)
        elif language == "java":
            actual_output, error = execute_java(code, input_str)
        elif language == "c":
            actual_output, error = execute_c(code, input_str)
        else:
            raise ValueError(f"Unsupported language: {language}")
        
        execution_time = time.time() - start_time
        
        if error:
            return {
                "input": input_data,
                "expected_output": expected_output,
                "actual_output": None,
                "passed": False,
                "error": error,
                "execution_time": execution_time
            }
        
        # Compare outputs with normalization
        passed = compare_outputs(actual_output, expected_output)
        
        return {
            "input": input_data,
            "expected_output": expected_output,
            "actual_output": actual_output,
            "passed": passed,
            "error": None,
            "execution_time": execution_time
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "input": input_data,
            "expected_output": expected_output,
            "actual_output": None,
            "passed": False,
            "error": str(e),
            "execution_time": execution_time
        }


def convert_input_format(input_data: str) -> str:
    """
    Convert JSON input to line-by-line format for stdin.
    
    Examples:
        {"nums": [2, 7, 11, 15], "target": 9} -> "2 7 11 15\n9"
        {"x": 123} -> "123"
        {"s": "hello"} -> "hello"
        
    Args:
        input_data: Input string (JSON or plain text)
        
    Returns:
        Formatted input string for stdin
    """
    try:
        # Try to parse as JSON
        data = json.loads(input_data)
        
        if isinstance(data, dict):
            # Convert dictionary values to lines
            lines = []
            for value in data.values():
                if isinstance(value, list):
                    # Convert list to space-separated values
                    lines.append(' '.join(map(str, value)))
                else:
                    lines.append(str(value))
            return '\n'.join(lines)
        elif isinstance(data, list):
            # If it's a list, convert to space-separated
            return ' '.join(map(str, data))
        else:
            # Single value
            return str(data)
    except json.JSONDecodeError:
        # Not JSON, return as-is
        return input_data


def execute_python(code: str, input_data: str) -> tuple:
    """Execute Python code"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Run with timeout of 5 seconds
            result = subprocess.run(
                ['python3', temp_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8'
            )
            ic(result)
            
            if result.returncode != 0:
                return None, result.stderr
            
            return result.stdout, None
            
        finally:
            os.unlink(temp_file)
            
    except subprocess.TimeoutExpired:
        return None, "Execution timed out (5 seconds limit)"
    except Exception as e:
        return None, str(e)


def execute_javascript(code: str, input_data: str) -> tuple:
    """Execute JavaScript code"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Run with Node.js with timeout of 5 seconds
            result = subprocess.run(
                ['node', temp_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                return None, result.stderr
            
            return result.stdout, None
            
        finally:
            os.unlink(temp_file)
            
    except subprocess.TimeoutExpired:
        return None, "Execution timed out (5 seconds limit)"
    except FileNotFoundError:
        return None, "Node.js not found. Please install Node.js to run JavaScript code."
    except Exception as e:
        return None, str(e)


def execute_cpp(code: str, input_data: str) -> tuple:
    """Execute C++ code"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False, encoding='utf-8') as f:
            f.write(code)
            source_file = f.name
        
        # Compile
        executable = source_file.replace('.cpp', '.exe' if os.name == 'nt' else '')
        
        try:
            compile_result = subprocess.run(
                ['g++', source_file, '-o', executable],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8'
            )
            
            if compile_result.returncode != 0:
                return None, f"Compilation error: {compile_result.stderr}"
            
            # Run
            result = subprocess.run(
                [executable],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                return None, result.stderr
            
            return result.stdout, None
            
        finally:
            if os.path.exists(source_file):
                os.unlink(source_file)
            if os.path.exists(executable):
                os.unlink(executable)
                
    except subprocess.TimeoutExpired:
        return None, "Execution timed out"
    except FileNotFoundError:
        return None, "g++ compiler not found. Please install GCC to compile C++ code."
    except Exception as e:
        return None, str(e)


def execute_java(code: str, input_data: str) -> tuple:
    """Execute Java code"""
    try:
        # Extract class name from code
        import re
        match = re.search(r'public\s+class\s+(\w+)', code)
        if not match:
            return None, "No public class found in Java code"
        
        class_name = match.group(1)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            java_file = os.path.join(temp_dir, f"{class_name}.java")
            
            with open(java_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Compile
            compile_result = subprocess.run(
                ['javac', java_file],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=temp_dir,
                encoding='utf-8'
            )
            
            if compile_result.returncode != 0:
                return None, f"Compilation error: {compile_result.stderr}"
            
            # Run
            result = subprocess.run(
                ['java', class_name],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5,
                cwd=temp_dir,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                return None, result.stderr
            
            return result.stdout, None
            
    except subprocess.TimeoutExpired:
        return None, "Execution timed out"
    except FileNotFoundError:
        return None, "Java compiler not found. Please install JDK to compile Java code."
    except Exception as e:
        return None, str(e)


def execute_c(code: str, input_data: str) -> tuple:
    """Execute C code"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False, encoding='utf-8') as f:
            f.write(code)
            source_file = f.name
        
        # Compile
        executable = source_file.replace('.c', '.exe' if os.name == 'nt' else '')
        
        try:
            compile_result = subprocess.run(
                ['gcc', source_file, '-o', executable],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8'
            )
            
            if compile_result.returncode != 0:
                return None, f"Compilation error: {compile_result.stderr}"
            
            # Run
            result = subprocess.run(
                [executable],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                return None, result.stderr
            
            return result.stdout, None
            
        finally:
            if os.path.exists(source_file):
                os.unlink(source_file)
            if os.path.exists(executable):
                os.unlink(executable)
                
    except subprocess.TimeoutExpired:
        return None, "Execution timed out"
    except FileNotFoundError:
        return None, "gcc compiler not found. Please install GCC to compile C code."
    except Exception as e:
        return None, str(e)
