import os
import fnmatch

MAX_CHARACTERS = 10000

def display_project_structure_with_content(startpath='.'):
    excluded_dirs = ['env', 'media', '.git', '__pycache__', 'migrations', 'static']  # Add more if needed
    text_file_patterns = ['*.py', '*.html', '*.css', '*.json', '*.yaml', '*.yml']

    for root, dirs, files in os.walk(startpath):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]  # Modify dirs in-place

        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        print('{}{}/'.format(indent, os.path.basename(root)))

        subindent = ' ' * 4 * (level + 1)
        for filename in files:
            if any(fnmatch.fnmatch(filename, pattern) for pattern in text_file_patterns):
                filepath = os.path.join(root, filename)
                print(f"{subindent}{filename}:")
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:  # Handle encoding
                        content = f.read()
                        # Limit content to avoid huge outputs:
                        shortened_content = content[:MAX_CHARACTERS] + "..." if len(content) > MAX_CHARACTERS else content
                        print(f"{subindent*2}{shortened_content.strip()}") # Added another indent and strip
                except UnicodeDecodeError:
                    print(f"{subindent*2}[Binary or undecodable file]")
                except Exception as e: # Catch other potential errors
                    print(f"{subindent*2}[Error reading file: {e}]")
                print("-" * 20) # Separator between files

if __name__ == "__main__":
    display_project_structure_with_content()