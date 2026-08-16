import pytest
from backend.app.core.security import SecretVault, hash_token


def test_secret_vault_encryption_decryption():
    vault = SecretVault("test_master_secret_key_32_bytes_test!")
    plain_text = "super_secret_brain_password_123"
    
    encrypted = vault.encrypt(plain_text)
    assert encrypted != plain_text
    assert len(encrypted) > 20
    
    decrypted = vault.decrypt(encrypted)
    assert decrypted == plain_text


def test_secret_vault_empty_and_corrupt():
    vault = SecretVault("test_key")
    assert vault.encrypt("") == ""
    assert vault.decrypt("") == ""
    assert vault.decrypt("invalid_corrupt_cipher") == ""


def test_token_hashing():
    t1 = "token_abc"
    t2 = "token_abc"
    t3 = "token_xyz"
    assert hash_token(t1) == hash_token(t2)
    assert hash_token(t1) != hash_token(t3)
