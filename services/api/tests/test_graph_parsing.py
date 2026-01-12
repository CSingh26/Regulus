from regulus_api.graph.parsers import extract_imports


def test_extract_imports_python() -> None:
    code = """
import os
from .utils import helper
from pkg.module import thing
"""
    imports = extract_imports("python", code)
    assert "os" in imports
    assert ".utils" in imports
    assert "pkg.module" in imports


def test_extract_imports_javascript() -> None:
    code = """
import foo from './foo'
const bar = require('../bar')
"""
    imports = extract_imports("javascript", code)
    assert "./foo" in imports
    assert "../bar" in imports
