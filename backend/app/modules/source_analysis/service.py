import ast
from pathlib import Path


def analyze_python_file(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        return {
            "status": "not_found",
            "file": path.name,
            "imports": [],
            "functions": [],
            "classes": [],
        }

    try:
        source_code = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        tree = ast.parse(source_code)

        imports = []
        functions = []
        classes = []

        for node in tree.body:

            # Detect imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

            # Detect top-level functions
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                    }
                )

            # Detect classes
            elif isinstance(node, ast.ClassDef):
                methods = []

                for child in node.body:
                    if isinstance(
                        child,
                        (ast.FunctionDef, ast.AsyncFunctionDef),
                    ):
                        methods.append(
                            {
                                "name": child.name,
                                "line": child.lineno,
                            }
                        )

                classes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "methods": methods,
                    }
                )

        return {
            "status": "success",
            "file": path.name,
            "imports": imports,
            "functions": functions,
            "classes": classes,
        }

    except SyntaxError as error:
        return {
            "status": "syntax_error",
            "file": path.name,
            "imports": [],
            "functions": [],
            "classes": [],
            "message": str(error),
        }

    except Exception as error:
        return {
            "status": "error",
            "file": path.name,
            "imports": [],
            "functions": [],
            "classes": [],
            "message": str(error),
        }

def analyze_python_directory(directory_path: str) -> list[dict]:
    directory = Path(directory_path)

    if not directory.exists() or not directory.is_dir():
        return []

    results = []

    for file_path in directory.rglob("*.py"):
        result = analyze_python_file(str(file_path))
        results.append(result)

    return results