#!/usr/bin/env python3
\"\"\"
Script to fix the escaped triple quotes in chatbot.py
\"\"\"

def fix_escaped_quotes(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace incorrectly escaped triple quotes
    content = content.replace('\\\"\\\"\\\"Main function\\\"\\\"\\\"', '\"\"\"Main function\"\"\"')
    
    # Also fix other escaped triple quotes that might be in the docstring
    content = content.replace('\\\"\\\"\\\"', '\"\"\"')
    
    # Fix other escaped quotes in strings
    content = content.replace('\\\"', '\"')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == \"__main__\":
    fix_escaped_quotes('core/chatbot.py')
    print(\"Fixed escaped quotes in core/chatbot.py\")