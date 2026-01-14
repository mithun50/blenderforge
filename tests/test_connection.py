"""Tests for BlenderConnection class."""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestBlenderConnection:
    """Tests for the BlenderConnection dataclass and its methods."""

    def test_connection_init_defaults(self):
        """Test BlenderConnection initializes with correct defaults."""
        from blenderforge.server import BlenderConnection

        conn = BlenderConnection(host="localhost", port=9876)
        assert conn.host == "localhost"
        assert conn.port == 9876
        assert conn.sock is None
        assert conn.auth_token is None
        assert conn.max_retries == 3
        assert conn.retry_delay == 1.0

    def test_connection_custom_values(self):
        """Test BlenderConnection with custom values."""
        from blenderforge.server import BlenderConnection

        conn = BlenderConnection(
            host="192.168.1.1",
            port=9999,
            max_retries=5,
            retry_delay=2.0,
        )
        assert conn.host == "192.168.1.1"
        assert conn.port == 9999
        assert conn.max_retries == 5
        assert conn.retry_delay == 2.0

    @patch("socket.socket")
    def test_connect_success(self, mock_socket_class):
        """Test successful connection."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        conn = BlenderConnection(host="localhost", port=9876)
        result = conn.connect()

        assert result is True
        assert conn.sock is not None
        mock_socket.connect.assert_called_once_with(("localhost", 9876))

    @patch("socket.socket")
    def test_connect_already_connected(self, mock_socket_class):
        """Test connect when already connected returns True."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        conn = BlenderConnection(host="localhost", port=9876)
        conn.sock = mock_socket

        result = conn.connect()

        assert result is True
        mock_socket_class.assert_not_called()

    @patch("socket.socket")
    def test_connect_failure_retry(self, mock_socket_class):
        """Test connection retries on failure."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        mock_socket.connect.side_effect = ConnectionRefusedError()
        mock_socket_class.return_value = mock_socket

        conn = BlenderConnection(host="localhost", port=9876, max_retries=2, retry_delay=0.01)
        result = conn.connect()

        assert result is False
        assert conn.sock is None
        assert mock_socket.connect.call_count == 2

    @patch("socket.socket")
    def test_connect_timeout(self, mock_socket_class):
        """Test connection timeout handling."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        mock_socket.connect.side_effect = TimeoutError()
        mock_socket_class.return_value = mock_socket

        conn = BlenderConnection(host="localhost", port=9876, max_retries=1, retry_delay=0.01)
        result = conn.connect()

        assert result is False
        assert conn.sock is None

    def test_disconnect(self):
        """Test disconnect closes socket."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        conn = BlenderConnection(host="localhost", port=9876)
        conn.sock = mock_socket

        conn.disconnect()

        mock_socket.close.assert_called_once()
        assert conn.sock is None

    def test_disconnect_no_socket(self):
        """Test disconnect when no socket exists."""
        from blenderforge.server import BlenderConnection

        conn = BlenderConnection(host="localhost", port=9876)
        conn.disconnect()  # Should not raise
        assert conn.sock is None

    def test_disconnect_error_handling(self):
        """Test disconnect handles errors gracefully."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        mock_socket.close.side_effect = Exception("Close failed")
        conn = BlenderConnection(host="localhost", port=9876)
        conn.sock = mock_socket

        conn.disconnect()  # Should not raise
        assert conn.sock is None

    @patch("socket.socket")
    def test_send_command_not_connected(self, mock_socket_class):
        """Test send_command when not connected."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        mock_socket.connect.side_effect = ConnectionRefusedError()
        mock_socket_class.return_value = mock_socket

        conn = BlenderConnection(host="localhost", port=9876, max_retries=1, retry_delay=0.01)

        with pytest.raises(ConnectionError, match="Not connected"):
            conn.send_command("test_command")

    @patch("socket.socket")
    def test_send_command_success(self, mock_socket_class):
        """Test successful command sending."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        response = {"status": "success", "result": {"data": "test"}}
        mock_socket.recv.return_value = json.dumps(response).encode("utf-8")

        conn = BlenderConnection(host="localhost", port=9876)
        conn.sock = mock_socket

        result = conn.send_command("test_command", {"param": "value"})

        assert result == {"data": "test"}
        mock_socket.sendall.assert_called_once()

    @patch("socket.socket")
    def test_send_command_error_response(self, mock_socket_class):
        """Test command with error response from Blender."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        response = {"status": "error", "message": "Something went wrong"}
        mock_socket.recv.return_value = json.dumps(response).encode("utf-8")

        conn = BlenderConnection(host="localhost", port=9876)
        conn.sock = mock_socket

        with pytest.raises(Exception, match="Something went wrong"):
            conn.send_command("test_command")

    @patch("socket.socket")
    def test_send_command_timeout(self, mock_socket_class):
        """Test command timeout handling."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.side_effect = TimeoutError()

        conn = BlenderConnection(host="localhost", port=9876)
        conn.sock = mock_socket

        with pytest.raises(Exception, match="Timeout"):
            conn.send_command("test_command")

        assert conn.sock is None  # Socket should be cleared

    @patch("socket.socket")
    def test_send_command_with_auth_token(self, mock_socket_class):
        """Test command includes auth token when set."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        response = {"status": "success", "result": {}}
        mock_socket.recv.return_value = json.dumps(response).encode("utf-8")

        conn = BlenderConnection(host="localhost", port=9876)
        conn.sock = mock_socket
        conn.auth_token = "secret_token"

        conn.send_command("test_command")

        # Verify auth token was included
        call_args = mock_socket.sendall.call_args[0][0]
        sent_data = json.loads(call_args.decode("utf-8"))
        assert sent_data["auth_token"] == "secret_token"


class TestReceiveFullResponse:
    """Tests for the receive_full_response method."""

    def test_receive_complete_json(self):
        """Test receiving complete JSON in one chunk."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        response = {"status": "success", "result": {"key": "value"}}
        mock_socket.recv.side_effect = [json.dumps(response).encode("utf-8"), b""]

        conn = BlenderConnection(host="localhost", port=9876)
        result = conn.receive_full_response(mock_socket)

        assert json.loads(result.decode("utf-8")) == response

    def test_receive_chunked_json(self):
        """Test receiving JSON in multiple chunks."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        response = {"status": "success", "result": {"key": "value"}}
        full_json = json.dumps(response).encode("utf-8")

        # Split into chunks
        chunk1 = full_json[:10]
        chunk2 = full_json[10:]

        mock_socket.recv.side_effect = [chunk1, chunk2]

        conn = BlenderConnection(host="localhost", port=9876)
        result = conn.receive_full_response(mock_socket)

        assert json.loads(result.decode("utf-8")) == response

    def test_receive_empty_response(self):
        """Test handling empty response."""
        from blenderforge.server import BlenderConnection

        mock_socket = MagicMock()
        mock_socket.recv.return_value = b""

        conn = BlenderConnection(host="localhost", port=9876)

        with pytest.raises(Exception, match="Connection closed|No data"):
            conn.receive_full_response(mock_socket)
