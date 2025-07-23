import os

EXCLUDE_DIRS = {"venv", "__pycache__", ".git", ".mypy_cache"}
TARGET_EXTENSIONS = {".py"}

# Replace "auth_id" with "auth_id"
OLD = '"auth_id"'
NEW = '"auth_id"'


def should_process_file(filepath: str) -> bool:
    """Check if the file should be processed based on its extension."""
    return os.path.splitext(filepath)[1] in TARGET_EXTENSIONS


def replace_in_file(filepath: str) -> bool:
    """Replace OLD with NEW in the given file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    if OLD not in content:
        return False  # Nothing to replace

    new_content = content.replace(OLD, NEW)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        print(f"Error writing {filepath}: {e}")
        return False

    print(f"✅ Updated: {filepath}")
    return True


def walk_and_replace(root_dir: str):
    """Walk through all files and perform replacements."""
    for root, dirs, files in os.walk(root_dir):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            filepath = os.path.join(root, file)
            if should_process_file(filepath):
                replace_in_file(filepath)


if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))  # Get full path
    walk_and_replace(base_path)

