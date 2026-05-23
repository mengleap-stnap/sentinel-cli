import unittest
import os
import tempfile
import shutil
from pathlib import Path

# Import the class to test
from sentinelapex.security import SecurityManager

class TestSecurityManager(unittest.TestCase):
    
    def setUp(self):
        """
        Create a temporary directory for testing to avoid polluting 
        the user's actual home directory.
        """
        self.test_dir = tempfile.mkdtemp()
        self.original_home = Path.home()
        
        # We need to mock the home directory or inject the path into SecurityManager
        # Since SecurityManager hardcodes Path.home(), we'll subclass it for testing
        # or modify the instance variable if possible. 
        # For this simple test, we will let it use the real home but clean up after?
        # No, that's dangerous. Let's patch Path.home or create a custom test class.
        
        # Better approach: Create a test-specific SecurityManager that accepts a path
        # But since the current implementation uses hardcoded Path.home(), 
        # we will test the logic by instantiating it and ensuring it creates files 
        # in a controlled way if we could inject the path.
        
        # Given the current implementation of SecurityManager in security.py:
        # It uses self.config_dir = Path.home() / ".sentinelapex"
        
        # To test safely without side effects, we can monkeypatch Path.home()
        self.patcher = unittest.mock.patch('pathlib.Path.home', return_value=Path(self.test_dir))
        self.mock_home = self.patcher.start()
        
        # Re-import or re-initialize to pick up the mocked home
        # Note: In a real scenario, dependency injection is better. 
        # Here we just instantiate after patching.
        self.sec_mgr = SecurityManager()

    def tearDown(self):
        """Clean up temporary directory."""
        self.patcher.stop()
        shutil.rmtree(self.test_dir)

    def test_master_key_creation(self):
        """Test that the master key file is created."""
        key_file = Path(self.test_dir) / ".sentinelapex" / "master.key"
        self.assertTrue(key_file.exists())
        self.assertEqual(os.stat(key_file).st_mode & 0o777, 0o600) # Check permissions

    def test_encrypt_decrypt_cycle(self):
        """Test that a token can be encrypted and then decrypted back to original."""
        original_token = "sk-test-1234567890abcdef"
        
        encrypted = self.sec_mgr.encrypt_token(original_token)
        self.assertNotEqual(original_token, encrypted)
        self.assertIsNotNone(encrypted)
        
        decrypted = self.sec_mgr.decrypt_token(encrypted)
        self.assertEqual(original_token, decrypted)

    def test_decrypt_empty_string(self):
        """Test that decrypting an empty string returns empty string."""
        result = self.sec_mgr.decrypt_token("")
        self.assertEqual(result, "")

    def test_decrypt_invalid_token(self):
        """Test that decrypting garbage data returns empty string instead of crashing."""
        result = self.sec_mgr.decrypt_token("this-is-not-valid-encrypted-data")
        self.assertEqual(result, "")

    def test_mask_key_short(self):
        """Test masking of short keys."""
        masked = self.sec_mgr.mask_key("123")
        self.assertEqual(masked, "****")

    def test_mask_key_long(self):
        """Test masking of long keys."""
        key = "sk-proj-1234567890abcdef-end"
        masked = self.sec_mgr.mask_key(key)
        self.assertTrue(masked.startswith("sk-p"))
        self.assertTrue(masked.endswith("-end"))
        self.assertIn("...", masked)

    def test_mask_key_empty(self):
        """Test masking of empty key."""
        masked = self.sec_mgr.mask_key("")
        self.assertEqual(masked, "Not Set")

if __name__ == '__main__':
    import unittest.mock
    unittest.main()