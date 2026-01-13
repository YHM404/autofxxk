"""
配置加载模块
负责加载和管理系统配置
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """模型配置"""

    provider: str
    id: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None

    def get_model_instance(self):
        """根据配置创建模型实例"""
        if self.provider == "openai":
            from agno.models.openai import OpenAIChat

            params = {
                "id": self.id,
                "temperature": self.temperature,
            }
            if self.max_tokens:
                params["max_tokens"] = self.max_tokens
            if self.api_key:
                params["api_key"] = self.api_key
            if self.base_url:
                params["base_url"] = self.base_url
            return OpenAIChat(**params)

        elif self.provider == "anthropic":
            from agno.models.anthropic import Claude

            params = {
                "id": self.id,
                "temperature": self.temperature,
            }
            if self.max_tokens:
                params["max_tokens"] = self.max_tokens
            if self.api_key:
                params["api_key"] = self.api_key
            return Claude(**params)

        elif self.provider == "openai-compatible":
            # 兼容 OpenAI API 的其他提供商
            from agno.models.openai import OpenAIChat

            params = {
                "id": self.id,
                "temperature": self.temperature,
            }
            if self.max_tokens:
                params["max_tokens"] = self.max_tokens
            if self.api_key:
                params["api_key"] = self.api_key
            if self.base_url:
                params["base_url"] = self.base_url
            return OpenAIChat(**params)

        elif self.provider == "anthropic-compatible":
            # 兼容 Anthropic API 的其他提供商（第三方 Anthropic API）
            from agno.models.anthropic import Claude

            params = {
                "id": self.id,
                "temperature": self.temperature,
            }
            if self.max_tokens:
                params["max_tokens"] = self.max_tokens
            if self.api_key:
                params["api_key"] = self.api_key
            # base_url 需要通过 client_params 传递
            if self.base_url:
                params["client_params"] = {"base_url": self.base_url}
            return Claude(**params)

        else:
            raise ValueError(f"不支持的模型提供商: {self.provider}")


@dataclass
class ToolConfig:
    """工具配置"""

    enabled: bool = True
    params: Dict[str, Any] = None

    def __post_init__(self):
        if self.params is None:
            self.params = {}


@dataclass
class HistoryConfig:
    """对话历史配置"""

    enabled: bool = True
    num_runs: Optional[int] = None
    num_messages: Optional[int] = None


@dataclass
class AgentConfig:
    """Agent 配置"""

    name: str
    role: str
    markdown: bool = True
    debug_mode: bool = False
    tools: Dict[str, Dict[str, Any]] = None
    history: Optional[HistoryConfig] = None

    def __post_init__(self):
        if self.tools is None:
            self.tools = {}


class Config:
    """配置管理器"""

    _instance = None
    _config: Dict[str, Any] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self.load()

    def load(self, config_path: Optional[str] = None):
        """加载配置文件"""
        if config_path is None:
            # 默认配置文件路径
            config_path = Path(__file__).parent / "config.yaml"

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项

        Args:
            key: 配置键，支持点号分隔的路径，如 "models.default.id"
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_model_config(self, agent_type: str = "default") -> ModelConfig:
        """获取模型配置

        Args:
            agent_type: Agent 类型，如 "technical_analysis", "macro_analysis"

        Returns:
            ModelConfig 对象
        """
        model_config = self.get(f"models.{agent_type}")
        if model_config is None:
            model_config = self.get("models.default")

        return ModelConfig(
            provider=model_config.get("provider", "openai"),
            id=model_config.get("id", "gpt-4o"),
            temperature=model_config.get("temperature", 0.7),
            max_tokens=model_config.get("max_tokens"),
            api_key=model_config.get("api_key"),
            base_url=model_config.get("base_url"),
        )

    def get_agent_config(self, agent_type: str) -> AgentConfig:
        """获取 Agent 配置

        Args:
            agent_type: Agent 类型，如 "technical_analysis"

        Returns:
            AgentConfig 对象
        """
        agent_config = self.get(f"agents.{agent_type}", {})

        # 解析历史配置
        history_config = None
        if "history" in agent_config:
            history_data = agent_config["history"]
            history_config = HistoryConfig(
                enabled=history_data.get("enabled", True),
                num_runs=history_data.get("num_runs"),
                num_messages=history_data.get("num_messages"),
            )

        return AgentConfig(
            name=agent_config.get("name", "Agent"),
            role=agent_config.get("role", "AI Assistant"),
            markdown=agent_config.get("markdown", True),
            debug_mode=agent_config.get("debug_mode", False),
            tools=agent_config.get("tools", {}),
            history=history_config,
        )

    def get_tool_config(self, agent_type: str, tool_name: str) -> Dict[str, Any]:
        """获取工具配置

        Args:
            agent_type: Agent 类型
            tool_name: 工具名称，如 "yfinance", "duckduckgo"

        Returns:
            工具配置字典
        """
        tool_config = self.get(f"agents.{agent_type}.tools.{tool_name}", {})
        return tool_config

    def get_api_key(self, provider: str = "openai") -> str:
        """获取 API Key

        Args:
            provider: 提供商名称，如 "openai", "anthropic"

        优先从环境变量读取，其次从配置文件读取
        """
        # 环境变量名映射
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "openai-compatible": "OPENAI_API_KEY",
        }

        env_var = env_var_map.get(provider, f"{provider.upper()}_API_KEY")
        api_key = os.getenv(env_var)

        if not api_key:
            # 从配置文件读取
            api_key = self.get(f"system.{provider}_api_key")

        if not api_key:
            raise ValueError(
                f"未找到 {env_var}。"
                f"请设置环境变量或在配置文件中配置 system.{provider}_api_key"
            )

        return api_key

    def get_openai_api_key(self) -> str:
        """获取 OpenAI API Key（向后兼容）"""
        return self.get_api_key("openai")

    def get_system_config(self, key: str, default: Any = None) -> Any:
        """获取系统配置

        Args:
            key: 配置键，如 "logging.level"
            default: 默认值

        Returns:
            配置值
        """
        return self.get(f"system.{key}", default)

    def get_analysis_config(self, key: str, default: Any = None) -> Any:
        """获取分析配置

        Args:
            key: 配置键，如 "defaults.time_range"
            default: 默认值

        Returns:
            配置值
        """
        return self.get(f"analysis.{key}", default)

    def is_tool_enabled(self, agent_type: str, tool_name: str) -> bool:
        """检查工具是否启用

        Args:
            agent_type: Agent 类型
            tool_name: 工具名称

        Returns:
            是否启用
        """
        return self.get(f"agents.{agent_type}.tools.{tool_name}.enabled", False)

    def reload(self):
        """重新加载配置文件"""
        self._config = None
        self.load()

    def __repr__(self) -> str:
        return f"Config(loaded={self._config is not None})"


# 全局配置实例
config = Config()


def get_config() -> Config:
    """获取配置实例"""
    return config


# 便捷函数
def get_model_config(agent_type: str = "default") -> ModelConfig:
    """获取模型配置"""
    return config.get_model_config(agent_type)


def get_agent_config(agent_type: str) -> AgentConfig:
    """获取 Agent 配置"""
    return config.get_agent_config(agent_type)


def get_tool_config(agent_type: str, tool_name: str) -> Dict[str, Any]:
    """获取工具配置"""
    return config.get_tool_config(agent_type, tool_name)


def get_openai_api_key() -> str:
    """获取 OpenAI API Key"""
    return config.get_openai_api_key()
