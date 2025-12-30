"""
启动配置验证器

验证系统启动所需的必需配置项，提供友好的错误提示。
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ConfigLevel(Enum):
    """配置级别"""
    REQUIRED = "required"      # 必需配置，缺少则无法启动
    RECOMMENDED = "recommended"  # 推荐配置，缺少会影响功能
    OPTIONAL = "optional"      # 可选配置，缺少不影响基本功能


@dataclass
class ConfigItem:
    """配置项"""
    key: str                    # 配置键名
    level: ConfigLevel          # 配置级别
    description: str            # 配置描述
    example: Optional[str] = None  # 配置示例
    help_url: Optional[str] = None  # 帮助链接
    validator: Optional[callable] = None  # 自定义验证函数


@dataclass
class ValidationResult:
    """验证结果"""
    success: bool               # 是否验证成功
    missing_required: List[ConfigItem]  # 缺少的必需配置
    missing_recommended: List[ConfigItem]  # 缺少的推荐配置
    invalid_configs: List[tuple[ConfigItem, str]]  # 无效的配置（配置项，错误信息）
    warnings: List[str]         # 警告信息


class StartupValidator:
    """启动配置验证器"""
    
    # 必需配置项
    REQUIRED_CONFIGS = [
        ConfigItem(
            key="MONGODB_HOST",
            level=ConfigLevel.REQUIRED,
            description="MongoDB主机地址",
            example="localhost"
        ),
        ConfigItem(
            key="MONGODB_PORT",
            level=ConfigLevel.REQUIRED,
            description="MongoDB端口",
            example="27017",
            validator=lambda v: v.isdigit() and 1 <= int(v) <= 65535
        ),
        ConfigItem(
            key="MONGODB_DATABASE",
            level=ConfigLevel.REQUIRED,
            description="MongoDB数据库名称",
            example="tradingagents"
        ),
        ConfigItem(
            key="REDIS_HOST",
            level=ConfigLevel.REQUIRED,
            description="Redis主机地址",
            example="localhost"
        ),
        ConfigItem(
            key="REDIS_PORT",
            level=ConfigLevel.REQUIRED,
            description="Redis端口",
            example="6379",
            validator=lambda v: v.isdigit() and 1 <= int(v) <= 65535
        ),
        ConfigItem(
            key="JWT_SECRET",
            level=ConfigLevel.REQUIRED,
            description="JWT密钥（用于生成认证令牌）",
            example="your-super-secret-jwt-key-change-in-production",
            validator=lambda v: len(v) >= 16
        ),
    ]
    
    # 推荐配置项
    RECOMMENDED_CONFIGS = [
        ConfigItem(
            key="DEEPSEEK_API_KEY",
            level=ConfigLevel.RECOMMENDED,
            description="DeepSeek API密钥（推荐，性价比高）",
            example="sk-xxx",
            help_url="https://platform.deepseek.com/"
        ),
        ConfigItem(
            key="DASHSCOPE_API_KEY",
            level=ConfigLevel.RECOMMENDED,
            description="阿里百炼API密钥（推荐，国产稳定）",
            example="sk-xxx",
            help_url="https://dashscope.aliyun.com/"
        ),
        ConfigItem(
            key="TUSHARE_TOKEN",
            level=ConfigLevel.RECOMMENDED,
            description="Tushare Token（推荐，专业A股数据）",
            example="xxx",
            help_url="https://tushare.pro/register?reg=tacn"
        ),
        ConfigItem(
            key="OPENAI_API_KEY",
            level=ConfigLevel.RECOMMENDED,
            description="OpenAI API密钥（可选，GPT-4等高级模型）",
            example="sk-xxx",
            help_url="https://platform.openai.com/"
        ),
    ]
    
    # 可选配置项（用于功能验证）
    OPTIONAL_CONFIGS = [
        ConfigItem(
            key="HOST",
            level=ConfigLevel.OPTIONAL,
            description="API服务监听地址",
            example="0.0.0.0"
        ),
        ConfigItem(
            key="PORT",
            level=ConfigLevel.OPTIONAL,
            description="API服务监听端口",
            example="8000",
            validator=lambda v: v.isdigit() and 1 <= int(v) <= 65535
        ),
        ConfigItem(
            key="DEBUG",
            level=ConfigLevel.OPTIONAL,
            description="调试模式",
            example="false"
        ),
    ]
    
    def __init__(self):
        self.result = ValidationResult(
            success=True,
            missing_required=[],
            missing_recommended=[],
            invalid_configs=[],
            warnings=[]
        )

    def _is_valid_api_key(self, api_key: str) -> bool:
        """
        判断 API Key 是否有效（不是占位符）

        Args:
            api_key: 待验证的 API Key

        Returns:
            bool: True 表示有效，False 表示无效或占位符
        """
        if not api_key:
            return False

        # 去除首尾空格和引号
        api_key = api_key.strip().strip('"').strip("'")

        # 检查是否为空
        if not api_key:
            return False

        # 检查是否为占位符（前缀）
        if api_key.startswith('your_') or api_key.startswith('your-'):
            return False

        # 检查是否为占位符（后缀）
        if api_key.endswith('_here') or api_key.endswith('-here'):
            return False

        # 检查长度（大多数 API Key 都 > 10 个字符）
        if len(api_key) <= 10:
            return False

        return True

    def validate(self) -> ValidationResult:
        """
        验证配置
        
        Returns:
            ValidationResult: 验证结果
        """
        logger.info("开始验证启动配置...")
        
        # 验证必需配置
        self._validate_required_configs()
        
        # 验证推荐配置
        self._validate_recommended_configs()
        
        # 验证可选配置（仅验证格式，不要求必须存在）
        self._validate_optional_configs()
        
        # 检查安全配置
        self._check_security_configs()
        
        # 检查网络连通性
        self._check_network_connectivity()
        
        # 设置验证结果
        self.result.success = len(self.result.missing_required) == 0 and len(self.result.invalid_configs) == 0
        
        # 输出验证结果
        self._print_validation_result()
        
        return self.result
    
    def _validate_required_configs(self):
        """验证必需配置"""
        for config in self.REQUIRED_CONFIGS:
            value = os.getenv(config.key)
            
            if not value:
                self.result.missing_required.append(config)
                logger.error(f"❌ 缺少必需配置: {config.key}")
            elif config.validator and not config.validator(value):
                self.result.invalid_configs.append((config, "配置值格式不正确"))
                logger.error(f"❌ 配置格式错误: {config.key}")
            else:
                logger.debug(f"✅ {config.key}: 已配置")
    
    def _validate_recommended_configs(self):
        """验证推荐配置"""
        for config in self.RECOMMENDED_CONFIGS:
            value = os.getenv(config.key)

            if not value:
                self.result.missing_recommended.append(config)
                logger.warning(f"缺少推荐配置: {config.key}")
            elif not self._is_valid_api_key(value):
                # API Key 存在但是占位符，视为未配置
                self.result.missing_recommended.append(config)
                logger.warning(f"{config.key} 配置为占位符，视为未配置")
            else:
                logger.debug(f"{config.key}: 已配置")
    
    def _validate_optional_configs(self):
        """验证可选配置（仅验证格式）"""
        for config in self.OPTIONAL_CONFIGS:
            value = os.getenv(config.key)
            
            if value and config.validator and not config.validator(value):
                self.result.invalid_configs.append((config, "配置值格式不正确"))
                logger.warning(f"配置格式错误: {config.key}")
            elif value:
                logger.debug(f"{config.key}: {value}")
    
    def _check_security_configs(self):
        """检查安全配置"""
        # 检查JWT密钥是否使用默认值或弱密钥
        jwt_secret = os.getenv("JWT_SECRET", "")
        insecure_jwt_defaults = [
            "change-me-in-production",
            "your-super-secret-jwt-key-change-in-production",
            "",  # 空值也不安全
            "secret", "password", "123456",  # 常见弱密钥
        ]
        if jwt_secret in insecure_jwt_defaults or len(jwt_secret) < 16:
            self.result.warnings.append(
                f"⚠️  JWT_SECRET 使用不安全值（长度: {len(jwt_secret)}），生产环境请务必修改！"
                f"生成方式: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )

        # 检查CSRF密钥是否使用默认值或弱密钥
        csrf_secret = os.getenv("CSRF_SECRET", "")
        insecure_csrf_defaults = [
            "change-me-csrf-secret",
            "your-csrf-secret-key-change-in-production",
            "",  # 空值也不安全
            "secret", "password", "123456",  # 常见弱密钥
        ]
        if csrf_secret in insecure_csrf_defaults or len(csrf_secret) < 16:
            self.result.warnings.append(
                f"⚠️  CSRF_SECRET 使用不安全值（长度: {len(csrf_secret)}），生产环境请务必修改！"
                f"生成方式: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )

        # 检查是否在生产环境使用DEBUG模式
        debug = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes", "on")
        if not debug:
            logger.info("生产环境模式")
        else:
            logger.info("开发环境模式（DEBUG=true）")
    
    def _check_network_connectivity(self):
        """检查网络连通性和依赖服务"""
        logger.debug("检查网络连通性...")
        
        # 检查MongoDB连接配置
        mongo_host = os.getenv("MONGODB_HOST", "")
        mongo_port = os.getenv("MONGODB_PORT", "")
        
        if mongo_host and mongo_port:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((mongo_host, int(mongo_port)))
                sock.close()
                
                if result == 0:
                    logger.debug(f"MongoDB连接检测: {mongo_host}:{mongo_port} 可达")
                else:
                    self.result.warnings.append(
                        f"无法连接到MongoDB {mongo_host}:{mongo_port}，请检查服务是否启动"
                    )
            except Exception as e:
                logger.debug(f"MongoDB连接检测失败: {e}")
        
        # 检查Redis连接配置
        redis_host = os.getenv("REDIS_HOST", "")
        redis_port = os.getenv("REDIS_PORT", "")
        
        if redis_host and redis_port:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((redis_host, int(redis_port)))
                sock.close()
                
                if result == 0:
                    logger.debug(f"Redis连接检测: {redis_host}:{redis_port} 可达")
                else:
                    self.result.warnings.append(
                        f"无法连接到Redis {redis_host}:{redis_port}，请检查服务是否启动"
                    )
            except Exception as e:
                logger.debug(f"Redis连接检测失败: {e}")
    
    def _print_validation_result(self):
        """输出验证结果"""
        logger.info("\n" + "=" * 70)
        logger.info("TradingAgents-CN Configuration Validation Result")
        logger.info("=" * 70)
        
        # 必需配置
        if self.result.missing_required:
            logger.info("\nMissing required configurations:")
            for config in self.result.missing_required:
                logger.info(f"   - {config.key}")
                logger.info(f"     Description: {config.description}")
                if config.example:
                    logger.info(f"     Example: {config.example}")
                if config.help_url:
                    logger.info(f"     Help: {config.help_url}")
        else:
            logger.info("\nAll required configurations are complete")

        # 无效配置
        if self.result.invalid_configs:
            logger.info("\nInvalid configurations:")
            for config, error in self.result.invalid_configs:
                logger.info(f"   - {config.key}: {error}")
                if config.example:
                    logger.info(f"     Example: {config.example}")

        # 推荐配置
        if self.result.missing_recommended:
            logger.info("\nMissing recommended configurations (won't affect startup):")
            for config in self.result.missing_recommended:
                logger.info(f"   - {config.key}")
                logger.info(f"     Description: {config.description}")
                if config.help_url:
                    logger.info(f"     Get it from: {config.help_url}")

        # 警告信息
        if self.result.warnings:
            logger.info("\nSecurity warnings:")
            for warning in self.result.warnings:
                logger.info(f"   - {warning}")

        # 总结
        logger.info("\n" + "=" * 70)
        if self.result.success:
            logger.info("Configuration validation passed, system can start")
            if self.result.missing_recommended:
                logger.info("Tip: Configure recommended items for better functionality")
        else:
            logger.info("Configuration validation failed, please check the above items")
            logger.info("Configuration guide: docs/configuration_guide.md")
        logger.info("=" * 70 + "\n")
    
    def raise_if_failed(self):
        """如果验证失败则抛出异常"""
        if not self.result.success:
            error_messages = []
            
            if self.result.missing_required:
                error_messages.append(
                    f"缺少必需配置: {', '.join(c.key for c in self.result.missing_required)}"
                )
            
            if self.result.invalid_configs:
                error_messages.append(
                    f"配置格式错误: {', '.join(c.key for c, _ in self.result.invalid_configs)}"
                )
            
            raise ConfigurationError(
                "配置验证失败:\n" + "\n".join(f"  • {msg}" for msg in error_messages) +
                "\n\n请检查 .env 文件并参考 docs/configuration_guide.md"
            )


class ConfigurationError(Exception):
    """配置错误异常"""
    pass


def validate_startup_config() -> ValidationResult:
    """
    验证启动配置（便捷函数）
    
    Returns:
        ValidationResult: 验证结果
    
    Raises:
        ConfigurationError: 如果验证失败
    """
    validator = StartupValidator()
    result = validator.validate()
    validator.raise_if_failed()
    return result

