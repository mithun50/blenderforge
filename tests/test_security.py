"""Tests for security features."""

import os
from unittest.mock import MagicMock, patch

import pytest


class TestCodeSecurityValidation:
    """Tests for code security validation."""

    def test_validate_safe_code(self):
        """Test that safe Blender code passes validation."""
        from blenderforge.server import validate_code_security

        safe_codes = [
            "bpy.ops.mesh.primitive_cube_add()",
            "import bpy\nbpy.data.objects['Cube'].location = (1, 2, 3)",
            "import mathutils\nv = mathutils.Vector((1, 0, 0))",
            "import math\nangle = math.pi / 2",
            "import random\nx = random.random()",
            "import json\ndata = json.dumps({'key': 'value'})",
            "from collections import defaultdict\nd = defaultdict(list)",
        ]

        for code in safe_codes:
            is_safe, error = validate_code_security(code)
            assert is_safe, f"Code should be safe: {code}\nError: {error}"

    def test_block_os_system(self):
        """Test that os.system is blocked."""
        from blenderforge.server import validate_code_security

        code = "import os\nos.system('rm -rf /')"
        is_safe, error = validate_code_security(code)
        assert not is_safe
        assert "os.system" in error.lower() or "dangerous" in error.lower()

    def test_block_subprocess(self):
        """Test that subprocess is blocked."""
        from blenderforge.server import validate_code_security

        code = "import subprocess\nsubprocess.run(['ls'])"
        is_safe, error = validate_code_security(code)
        assert not is_safe
        assert "subprocess" in error.lower() or "dangerous" in error.lower()

    def test_block_eval(self):
        """Test that eval is blocked."""
        from blenderforge.server import validate_code_security

        code = "eval('print(1)')"
        is_safe, error = validate_code_security(code)
        assert not is_safe
        assert "eval" in error.lower() or "dangerous" in error.lower()

    def test_block_exec(self):
        """Test that exec is blocked."""
        from blenderforge.server import validate_code_security

        code = "exec('print(1)')"
        is_safe, error = validate_code_security(code)
        assert not is_safe
        assert "exec" in error.lower() or "dangerous" in error.lower()

    def test_block_file_write(self):
        """Test that file writing is blocked."""
        from blenderforge.server import validate_code_security

        codes = [
            "open('/etc/passwd', 'w').write('hacked')",
            "with open('file.txt', 'a') as f: f.write('data')",
        ]

        for code in codes:
            is_safe, error = validate_code_security(code)
            assert not is_safe, f"Code should be blocked: {code}"

    def test_block_file_deletion(self):
        """Test that file deletion is blocked."""
        from blenderforge.server import validate_code_security

        codes = [
            "import shutil\nshutil.rmtree('/home')",
            "import os\nos.remove('file.txt')",
            "import os\nos.unlink('file.txt')",
            "import os\nos.rmdir('directory')",
        ]

        for code in codes:
            is_safe, error = validate_code_security(code)
            assert not is_safe, f"Code should be blocked: {code}"

    def test_block_network_operations(self):
        """Test that network operations are blocked."""
        from blenderforge.server import validate_code_security

        codes = [
            "import socket\ns = socket.socket()",
            "import requests\nrequests.get('http://evil.com')",
            "import urllib.request\nurllib.request.urlopen('http://evil.com')",
        ]

        for code in codes:
            is_safe, error = validate_code_security(code)
            assert not is_safe, f"Code should be blocked: {code}"

    def test_block_dynamic_import(self):
        """Test that __import__ is blocked."""
        from blenderforge.server import validate_code_security

        code = "__import__('os').system('ls')"
        is_safe, error = validate_code_security(code)
        assert not is_safe

    def test_block_unauthorized_imports(self):
        """Test that unauthorized imports are blocked."""
        from blenderforge.server import validate_code_security

        codes = [
            "import sys",
            "import pickle",
            "from ctypes import *",
        ]

        for code in codes:
            is_safe, error = validate_code_security(code)
            assert not is_safe, f"Import should be blocked: {code}"

    def test_allowed_imports(self):
        """Test that allowed imports pass validation."""
        from blenderforge.server import ALLOWED_IMPORTS, validate_code_security

        for module in ALLOWED_IMPORTS:
            code = f"import {module}"
            is_safe, error = validate_code_security(code)
            assert is_safe, f"Import should be allowed: {module}\nError: {error}"


class TestCodeExecutionToggle:
    """Tests for code execution enable/disable."""

    @patch.dict(os.environ, {"BLENDERFORGE_ALLOW_CODE_EXECUTION": "false"})
    def test_code_execution_disabled(self):
        """Test that code execution can be disabled via environment variable."""
        # Need to reimport to pick up new environment variable
        import importlib

        import blenderforge.server as server_module

        # Reload to pick up environment change
        importlib.reload(server_module)

        is_safe, error = server_module.validate_code_security("bpy.ops.mesh.primitive_cube_add()")
        assert not is_safe
        assert "disabled" in error.lower()

        # Reset
        os.environ["BLENDERFORGE_ALLOW_CODE_EXECUTION"] = "true"
        importlib.reload(server_module)


class TestExecuteBlenderCodeSecurity:
    """Tests for execute_blender_code with security validation."""

    @patch("blenderforge.server.get_blender_connection")
    def test_execute_safe_code(self, mock_get_conn):
        """Test executing safe code passes through."""
        from blenderforge.server import execute_blender_code

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {"result": "Created cube"}
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = execute_blender_code(ctx, "bpy.ops.mesh.primitive_cube_add()")

        assert "successfully" in result.lower()
        mock_conn.send_command.assert_called_once()

    def test_execute_dangerous_code_blocked(self):
        """Test that dangerous code is blocked before execution."""
        from blenderforge.server import execute_blender_code

        ctx = MagicMock()
        result = execute_blender_code(ctx, "import os\nos.system('rm -rf /')")

        assert "security" in result.lower() or "validation failed" in result.lower()

    def test_execute_unauthorized_import_blocked(self):
        """Test that unauthorized imports are blocked."""
        from blenderforge.server import execute_blender_code

        ctx = MagicMock()
        result = execute_blender_code(ctx, "import sys\nprint(sys.path)")

        assert "security" in result.lower() or "not allowed" in result.lower()


class TestSecurityConstants:
    """Tests for security constants."""

    def test_dangerous_patterns_defined(self):
        """Test that dangerous patterns are defined."""
        from blenderforge.server import DANGEROUS_CODE_PATTERNS

        assert isinstance(DANGEROUS_CODE_PATTERNS, list)
        assert len(DANGEROUS_CODE_PATTERNS) > 0

    def test_allowed_imports_defined(self):
        """Test that allowed imports are defined."""
        from blenderforge.server import ALLOWED_IMPORTS

        assert isinstance(ALLOWED_IMPORTS, set)
        assert "bpy" in ALLOWED_IMPORTS
        assert "mathutils" in ALLOWED_IMPORTS
        assert "bmesh" in ALLOWED_IMPORTS

    def test_code_execution_enabled_default(self):
        """Test that code execution is enabled by default."""
        from blenderforge.server import CODE_EXECUTION_ENABLED

        # In test environment, DISABLE_TELEMETRY is set but not code execution
        assert CODE_EXECUTION_ENABLED is True
