from __future__ import annotations

import ast

from tree_sitter import Node, Tree
from tree_sitter_languages import get_parser

SUPPORTED_LANGUAGES = {"python", "javascript", "typescript", "tsx"}


def extract_imports(language: str, text: str) -> set[str]:
    if language == "python":
        return extract_python_imports(text)
    if language in {"javascript", "typescript", "tsx"}:
        return extract_js_imports(language, text)
    return set()


def extract_python_imports(text: str) -> set[str]:
    imports: set[str] = set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            prefix = "." * node.level
            if module:
                imports.add(f"{prefix}{module}")
            elif prefix:
                imports.add(prefix)

    imports.update(extract_python_imports_ts(text))
    return imports


def extract_python_imports_ts(text: str) -> set[str]:
    parser = get_parser("python")
    return extract_imports_from_tree(parser.parse(text.encode("utf-8")), text)


def extract_js_imports(language: str, text: str) -> set[str]:
    parser = get_parser(language)
    tree = parser.parse(text.encode("utf-8"))
    return extract_imports_from_tree(tree, text)


def extract_imports_from_tree(tree: Tree, source: str) -> set[str]:
    imports: set[str] = set()
    source_bytes = source.encode("utf-8")

    def walk(node: Node) -> None:
        if node.type == "import_statement":
            source_node = node.child_by_field_name("source")
            if source_node is not None:
                spec = normalize_string(node_text(source_node, source_bytes))
                if spec:
                    imports.add(spec)
        if node.type == "call_expression":
            function_node = node.child_by_field_name("function")
            if function_node is not None:
                func_name = node_text(function_node, source_bytes)
                if func_name in {"require", "import"}:
                    arguments = node.child_by_field_name("arguments")
                    if arguments is not None:
                        for child in arguments.children:
                            if child.type == "string":
                                spec = normalize_string(node_text(child, source_bytes))
                                if spec:
                                    imports.add(spec)
                                break
        for child in node.children:
            walk(child)

    walk(tree.root_node)
    return imports


def node_text(node: Node, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="ignore")


def normalize_string(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] in {'"', "'", "`"}:
        return value[1:-1]
    return value
