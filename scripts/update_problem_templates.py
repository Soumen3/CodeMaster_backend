"""
Script to update existing problems with code template metadata.

This adds function signatures and parameter information for dynamic code generation.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal
from app.database.models import Problem
import json


# Example problem configurations
PROBLEM_TEMPLATES = {
    "Two Sum": {
        "function_name": "twoSum",
        "parameters": {
            "nums": "list[int]",
            "target": "int"
        },
        "return_type": "list"
    },
    "Longest Substring Without Repeating Characters": {
        "function_name": "lengthOfLongestSubstring",
        "parameters": {
            "s": "str"
        },
        "return_type": "int"
    },
    "Add Two Numbers": {
        "function_name": "addTwoNumbers",
        "parameters": {
            "l1": "list[int]",
            "l2": "list[int]"
        },
        "return_type": "list"
    },
    "Median of Two Sorted Arrays": {
        "function_name": "findMedianSortedArrays",
        "parameters": {
            "nums1": "list[int]",
            "nums2": "list[int]"
        },
        "return_type": "float"
    },
    "Reverse Integer": {
        "function_name": "reverse",
        "parameters": {
            "x": "int"
        },
        "return_type": "int"
    },
    "Palindrome Number": {
        "function_name": "isPalindrome",
        "parameters": {
            "x": "int"
        },
        "return_type": "bool"
    },
    "Valid Parentheses": {
        "function_name": "isValid",
        "parameters": {
            "s": "str"
        },
        "return_type": "bool"
    },
    "Merge Two Sorted Lists": {
        "function_name": "mergeTwoLists",
        "parameters": {
            "list1": "list[int]",
            "list2": "list[int]"
        },
        "return_type": "list"
    }
}


def update_problems():
    """Update existing problems with template metadata."""
    db = SessionLocal()
    
    try:
        problems = db.query(Problem).all()
        
        for problem in problems:
            print(f"Processing: {problem.title}")
            
            # Check if we have a template for this problem
            if problem.title in PROBLEM_TEMPLATES:
                template_config = PROBLEM_TEMPLATES[problem.title]
                
                problem.function_name = template_config["function_name"]
                problem.parameters = json.dumps(template_config["parameters"])
                problem.return_type = template_config["return_type"]
                
                print(f"  ✓ Updated: {template_config['function_name']}")
            else:
                # Set defaults
                if not problem.function_name:
                    problem.function_name = "solution"
                if not problem.parameters:
                    problem.parameters = json.dumps({"input": "str"})
                if not problem.return_type:
                    problem.return_type = "str"
                
                print(f"  ⚠ Default template applied")
        
        db.commit()
        print("\n✅ All problems updated successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Updating problems with code template metadata...\n")
    update_problems()
