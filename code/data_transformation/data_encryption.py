"""
数据加密模块

专注于数据加密、解密、密钥管理
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib
import base64
import logging

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """加密算法"""
    AES = "aes"
    RSA = "rsa"
    HASH = "hash"  # 哈希（不可逆）


@dataclass
class EncryptionResult:
    """加密结果"""
    encrypted_data: bytes
    algorithm: EncryptionAlgorithm
    key_id: Optional[str] = None
    iv: Optional[bytes] = None


class DataEncryption:
    """
    数据加密器
    
    专注于数据加密、解密、密钥管理
    """
    
    def __init__(self):
        self.keys: Dict[str, bytes] = {}
        self.encryption_history: List[EncryptionResult] = []
    
    def generate_key(self, key_id: str, algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES) -> bytes:
        """
        生成密钥
        
        Args:
            key_id: 密钥ID
            algorithm: 加密算法
            
        Returns:
            密钥
        """
        if algorithm == EncryptionAlgorithm.AES:
            # 生成AES密钥（32字节 = 256位）
            key = hashlib.sha256(f"{key_id}_{datetime.utcnow().timestamp()}".encode()).digest()
        elif algorithm == EncryptionAlgorithm.RSA:
            # RSA密钥生成（简化实现）
            key = hashlib.sha256(f"{key_id}_rsa_{datetime.utcnow().timestamp()}".encode()).digest()
        else:
            key = hashlib.sha256(f"{key_id}_{datetime.utcnow().timestamp()}".encode()).digest()
        
        self.keys[key_id] = key
        return key
    
    def encrypt(self, data: bytes, key_id: str,
               algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES) -> EncryptionResult:
        """
        加密数据
        
        Args:
            data: 要加密的数据
            key_id: 密钥ID
            algorithm: 加密算法
            
        Returns:
            加密结果
        """
        if key_id not in self.keys:
            self.generate_key(key_id, algorithm)
        
        key = self.keys[key_id]
        
        # 简化实现：使用XOR加密（实际应该使用真正的加密算法）
        if algorithm == EncryptionAlgorithm.AES:
            encrypted_data = self._xor_encrypt(data, key)
        elif algorithm == EncryptionAlgorithm.RSA:
            encrypted_data = self._xor_encrypt(data, key)
        else:
            encrypted_data = data
        
        result = EncryptionResult(
            encrypted_data=encrypted_data,
            algorithm=algorithm,
            key_id=key_id
        )
        
        self.encryption_history.append(result)
        return result
    
    def decrypt(self, encrypted_result: EncryptionResult) -> bytes:
        """
        解密数据
        
        Args:
            encrypted_result: 加密结果
            
        Returns:
            解密后的数据
        """
        if encrypted_result.key_id not in self.keys:
            raise ValueError(f"密钥不存在: {encrypted_result.key_id}")
        
        key = self.keys[encrypted_result.key_id]
        
        # 简化实现：使用XOR解密
        if encrypted_result.algorithm in [EncryptionAlgorithm.AES, EncryptionAlgorithm.RSA]:
            decrypted_data = self._xor_decrypt(encrypted_result.encrypted_data, key)
        else:
            decrypted_data = encrypted_result.encrypted_data
        
        return decrypted_data
    
    def _xor_encrypt(self, data: bytes, key: bytes) -> bytes:
        """XOR加密（简化实现）"""
        key_bytes = key * (len(data) // len(key) + 1)
        return bytes(a ^ b for a, b in zip(data, key_bytes))
    
    def _xor_decrypt(self, encrypted_data: bytes, key: bytes) -> bytes:
        """XOR解密（简化实现）"""
        return self._xor_encrypt(encrypted_data, key)  # XOR是对称的
    
    def hash_data(self, data: bytes, algorithm: str = 'sha256') -> str:
        """
        哈希数据（不可逆）
        
        Args:
            data: 要哈希的数据
            algorithm: 哈希算法（sha256, sha512, md5）
            
        Returns:
            哈希值（十六进制字符串）
        """
        if algorithm == 'sha256':
            hash_obj = hashlib.sha256(data)
        elif algorithm == 'sha512':
            hash_obj = hashlib.sha512(data)
        elif algorithm == 'md5':
            hash_obj = hashlib.md5(data)
        else:
            hash_obj = hashlib.sha256(data)
        
        return hash_obj.hexdigest()
    
    def encrypt_string(self, text: str, key_id: str,
                      algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES) -> str:
        """
        加密字符串
        
        Args:
            text: 要加密的文本
            key_id: 密钥ID
            algorithm: 加密算法
            
        Returns:
            加密后的Base64编码字符串
        """
        data = text.encode('utf-8')
        result = self.encrypt(data, key_id, algorithm)
        return base64.b64encode(result.encrypted_data).decode('utf-8')
    
    def decrypt_string(self, encrypted_text: str, key_id: str,
                      algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES) -> str:
        """
        解密字符串
        
        Args:
            encrypted_text: 加密的Base64编码字符串
            key_id: 密钥ID
            algorithm: 加密算法
            
        Returns:
            解密后的文本
        """
        encrypted_data = base64.b64decode(encrypted_text.encode('utf-8'))
        result = EncryptionResult(
            encrypted_data=encrypted_data,
            algorithm=algorithm,
            key_id=key_id
        )
        decrypted_data = self.decrypt(result)
        return decrypted_data.decode('utf-8')
    
    def get_encryption_stats(self) -> Dict[str, Any]:
        """
        获取加密统计
        
        Returns:
            加密统计
        """
        return {
            'total_keys': len(self.keys),
            'total_encryptions': len(self.encryption_history)
        }


def main():
    """主函数 - 示例用法"""
    encryption = DataEncryption()
    
    # 生成密钥
    key = encryption.generate_key('key1', EncryptionAlgorithm.AES)
    print(f"生成的密钥: {key.hex()[:16]}...")
    
    # 加密字符串
    text = "Hello, World!"
    encrypted = encryption.encrypt_string(text, 'key1')
    print(f"加密后的文本: {encrypted}")
    
    # 解密字符串
    decrypted = encryption.decrypt_string(encrypted, 'key1')
    print(f"解密后的文本: {decrypted}")


if __name__ == '__main__':
    main()
