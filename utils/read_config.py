from pathlib import Path
from typing import Optional, Union, Literal

from configobj import ConfigObj


class ReadConfig(object):
    """配置文件"""

    def __init__(
            self,
            config_path: Optional[Union[str, Path]] = None,
            default_configs: dict = None,
            decoder: Literal["gbk", "utf-8"] = "utf-8",
    ):
        """
        :param config_path: 配置文件的完整路径，默认为程序运行目录下的 '配置.ini'
        :param default_configs: 默认配置，格式为 {section: {option: {'default': default_value, 'value_type': type}}} 或 {section: {option: default_value}}
        :param decoder: 配置文件编码，可选 'gbk' 或 'utf-8'，默认为 'utf-8'
        """
        if decoder not in ("gbk", "utf-8"):
            raise ValueError("decoder 参数必须为 'gbk' 或 'utf-8'")
        self.decoder = decoder

        # 如果未指定 config_path，则默认使用程序运行目录下的 '配置.ini' 文件
        if config_path is None:
            self.config_path = Path("配置.ini")
        else:
            self.config_path = Path(config_path)

        # 判断文件是否存在
        if not self.config_path.exists():
            # 创建文件
            self.config_path.touch()
        self.config = ConfigObj(
            str(self.config_path), encoding=self.decoder, write_empty_values=True
        )

        # 初始化配置项，存储 option 到 section 的映射和 value_type
        self.option_sections = {}  # 存储每个 option 所在的 section，格式为 {option: section}
        self.value_types = {}  # 存储每个 option 的 value_type，格式为 {option: value_type}

        if default_configs:
            for section, options in default_configs.items():
                for option, option_info in options.items():
                    if isinstance(option_info, dict):
                        default_value = option_info.get("default", "")
                        value_type = option_info.get("value_type", str)
                    else:
                        # option_info 是直接的默认值
                        default_value = option_info
                        value_type = type(default_value)  # 默认类型
                    # 存储 option 到 section 的映射和 value_type
                    self.option_sections[option] = section
                    self.value_types[option] = value_type
                    # 如果配置文件中不存在该配置项，则使用默认值并写入配置文件
                    self.get(option, default=default_value)
        else:
            # 如果没有提供 default_configs，则默认空的 option_sections 和 value_types
            pass

    def get(self, option, default=None):
        """获取配置项的值，自动根据 value_type 转换类型"""
        section = self.option_sections.get(option)
        if section is None:
            raise KeyError(f"配置项 '{option}' 未在默认配置中定义。")
        try:
            result = self.config[section][option]
        except KeyError:
            result = str(default) if default is not None else ""
            if default is not None:
                self.set(option, default)
        # 获取 value_type，如果未指定，则默认为 str
        value_type = self.value_types.get(option, str)
        # 进行类型转换
        if value_type == int:
            try:
                result = int(result)
            except ValueError:
                result = default if default is not None else 0
        elif value_type == bool:
            result = result.lower() in ["yes", "true", "是", "1"]
        elif value_type == float:
            try:
                result = float(result)
            except ValueError:
                result = default if default is not None else 0.0
        else:
            # 默认为字符串
            result = str(result)
        return result

    def set(self, option, value):
        """更新或添加配置项"""
        section = self.option_sections.get(option)
        if section is None:
            raise KeyError(f"配置项 '{option}' 未在默认配置中定义。")
        if isinstance(value, bool):
            value = "是" if value else "否"
        elif not isinstance(value, str):
            value = str(value)
        if section not in self.config:
            self.config[section] = {}
        self.config[section][option] = value
        self.config.write()

    def get_sections(self):
        """获取所有的 section"""
        return self.config.sections

    def get_options(self, section):
        """获取指定 section 的所有 option"""
        return self.config[section].keys()

    def check_option(self, option, default=None):
        section = self.option_sections.get(option)
        if section is None:
            raise KeyError(f"配置项 '{option}' 未在默认配置中定义。")
        if section not in self.config or option not in self.config[section]:
            self.set(option, default)
            return False
        return True


if __name__ == "__main__":
    default_config = {
        "分组配置": {
            "名称": "默认分组",
            "ID": 0,
        },
        "其他配置": {
            "选项1": {"default": 1, "value_type": int},
            "选项2": {"default": 2.0, "value_type": float},
            "选项3": {"default": True, "value_type": bool},
        },
    }
    config = ReadConfig(default_configs=default_config)
    print(config.get("选项1"))
    config.set("选项1", 10)
    print(config.get("选项1"))
