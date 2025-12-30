"""
日志脱敏工具

用于在日志输出时自动脱敏敏感信息，包括：
- API密钥
- 密码
- JWT令牌
- 数据库连接字符串中的凭据
"""

import re
from typing import Any, Dict, List, Optional


class LogSanitizer:
    """日志脱敏器"""

    # 敏感字段名模式
    SENSITIVE_PATTERNS = [
        r'password',
        r'passwd',
        r'pwd',
        r'secret',
        r'token',
        r'api[_-]?key',
        r'apikey',
        r'authorization',
        r'auth[_-]?token',
        r'jwt',
        r'csrf',
        r'session[_-]?id',
        r'cookie',
        r'credential',
        r'private[_-]?key',
        r'access[_-]?token',
        r'refresh[_-]?token',
    ]

    # 敏感值模式
    SENSITIVE_VALUE_PATTERNS = [
        # Bearer token
        r'Bearer\s+[A-Za-z0-9\-._~+/]+=*',
        # JWT token
        r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
        # API key common formats
        r'sk-[a-zA-Z0-9]{20,}',
        r'ghp_[a-zA-Z0-9]{36}',
        r'gho_[a-zA-Z0-9]{36}',
        r'ghu_[a-zA-Z0-9]{36}',
        r'ghs_[a-zA-Z0-9]{36}',
        r'ghr_[a-zA-Z0-9]{36}',
        r'apikey-[a-zA-Z0-9]{32}',
        # MongoDB connection string
        r'mongodb://[^:]+:[^@]+@',
        # Redis connection string
        r'redis://:[^@]+@',
        # Generic key-value patterns
        r'["\']?[a-zA-Z_\-]*(?:password|secret|token|api[_-]?key)["\']?\s*[:=]\s*["\']?[^"\'\s,}]{8,}',
    ]

    # 需要保留部分信息的模式（如用于调试）
    KEEP_PREFIX_PATTERNS = {
        r'mongodb://[^:]+:': 'mongodb://***:***@',
        r'redis://:': 'redis://:***@',
    }

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any], mask_char: str = '*') -> Dict[str, Any]:
        """
        脱敏字典数据

        Args:
            data: 原始字典数据
            mask_char: 掩码字符，默认为 *

        Returns:
            脱敏后的字典
        """
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            # 检查键名是否为敏感字段
            if cls._is_sensitive_key(key):
                sanitized[key] = cls._mask_value(value, mask_char)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value, mask_char)
            elif isinstance(value, list):
                sanitized[key] = cls.sanitize_list(value, mask_char)
            else:
                sanitized[key] = value

        return sanitized

    @classmethod
    def sanitize_list(cls, data: List[Any], mask_char: str = '*') -> List[Any]:
        """
        脱敏列表数据

        Args:
            data: 原始列表数据
            mask_char: 掩码字符，默认为 *

        Returns:
            脱敏后的列表
        """
        if not isinstance(data, list):
            return data

        sanitized = []
        for item in data:
            if isinstance(item, dict):
                sanitized.append(cls.sanitize_dict(item, mask_char))
            elif isinstance(item, list):
                sanitized.append(cls.sanitize_list(item, mask_char))
            else:
                sanitized.append(item)

        return sanitized

    @classmethod
    def sanitize_string(cls, text: str, mask_char: str = '*', keep_length: bool = True) -> str:
        """
        脱敏字符串中的敏感信息

        Args:
            text: 原始文本
            mask_char: 掩码字符，默认为 *
            keep_length: 是否保持原长度，默认为True

        Returns:
            脱敏后的文本
        """
        if not isinstance(text, str):
            return text

        result = text

        # 处理连接字符串等需要保留前缀的情况
        for pattern, replacement in cls.KEEP_PREFIX_PATTERNS.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        # 处理敏感值模式
        for pattern in cls.SENSITIVE_VALUE_PATTERNS:
            def replace_match(match):
                matched_text = match.group(0)
                if keep_length:
                    return mask_char * len(matched_text)
                return mask_char * 8  # 固定8个星号

            result = re.sub(pattern, replace_match, result, flags=re.IGNORECASE)

        return result

    @classmethod
    def _is_sensitive_key(cls, key: str) -> bool:
        """
        判断键名是否为敏感字段

        Args:
            key: 键名

        Returns:
            是否为敏感字段
        """
        if not isinstance(key, str):
            return False

        key_lower = key.lower()
        for pattern in cls.SENSITIVE_PATTERNS:
            if re.search(pattern, key_lower, re.IGNORECASE):
                return True

        return False

    @classmethod
    def _mask_value(cls, value: Any, mask_char: str = '*') -> str:
        """
        对值进行脱敏处理

        Args:
            value: 原始值
            mask_char: 掩码字符

        Returns:
            脱敏后的字符串
        """
        if value is None:
            return None

        value_str = str(value)

        # 如果值很短，全部掩码
        if len(value_str) <= 4:
            return mask_char * len(value_str)

        # 否则保留前2位和后2位，中间全部掩码
        return value_str[:2] + mask_char * (len(value_str) - 4) + value_str[-2:]

    @classmethod
    def sanitize_log_message(cls, message: Any) -> str:
        """
        脱敏日志消息（便捷方法）

        Args:
            message: 日志消息（可以是任意类型）

        Returns:
            脱敏后的字符串
        """
        if isinstance(message, dict):
            message = cls.sanitize_dict(message)
        elif isinstance(message, list):
            message = cls.sanitize_list(message)

        message_str = str(message)
        return cls.sanitize_string(message_str)


# 全局单例
log_sanitizer = LogSanitizer()


def sanitize(data: Any) -> Any:
    """
    脱敏数据（便捷函数）

    Args:
        data: 任意类型的数据

    Returns:
        脱敏后的数据
    """
    if isinstance(data, dict):
        return LogSanitizer.sanitize_dict(data)
    elif isinstance(data, list):
        return LogSanitizer.sanitize_list(data)
    elif isinstance(data, str):
        return LogSanitizer.sanitize_string(data)
    else:
        return data


def safe_log(message: Any, mask_char: str = '*') -> str:
    """
    生成安全的日志消息（便捷函数）

    Args:
        message: 日志消息
        mask_char: 掩码字符

    Returns:
        脱敏后的日志字符串
    """
    return LogSanitizer.sanitize_log_message(message)
