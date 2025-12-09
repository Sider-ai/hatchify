import os
import re
import shlex
from typing import List
from typing import Optional, Tuple, TypedDict
from typing import cast, Union, Dict, Any

from loguru import logger
from openai import BaseModel
from strands.hooks import HookProvider, BeforeToolCallEvent, HookRegistry

from hatchify.common.settings.settings import get_hatchify_settings

settings = get_hatchify_settings()

BANNED_COMMANDS = [
    # 网络工具 - 可能用于数据泄露或下载恶意脚本
    'curl', 'wget', 'fetch', 'axel', 'aria2c',
    'httpie', 'xh', 'http-prompt',

    # 远程连接 - 可能建立反向 shell
    'ssh', 'scp', 'sftp', 'nc', 'netcat', 'telnet',
    'socat', 'ncat',

    # 代码执行 - 可能执行任意代码
    'eval', 'exec', 'source', '.', 'bash', 'sh', 'zsh',
    'fish', 'ksh', 'csh', 'tcsh',

    # 脚本解释器 - 可能执行恶意脚本
    'python', 'python2', 'python3', 'node', 'nodejs',
    'ruby', 'perl', 'php', 'lua', 'tclsh',

    # 浏览器 - 可能用于网络访问
    'chrome', 'firefox', 'safari', 'lynx', 'w3m', 'links',
    'elinks', 'chromium', 'opera',

    # 系统修改 - 可能修改权限或别名
    'alias', 'unalias', 'export', 'chmod', 'chown',
    'chgrp', 'su', 'sudo', 'doas',

    # 进程控制 - 可能干扰系统
    'kill', 'killall', 'pkill', 'reboot', 'shutdown', 'halt', 'poweroff',
]


class ValidationResult(BaseModel):
    is_valid: bool
    normalized_path: Optional[str] = None
    error: Optional[str] = None


class Command(TypedDict):
    command: str
    timeout: int
    work_dir: str


class SecurityFileHook(HookProvider):
    def __init__(self, workspace: str):
        super().__init__()
        self.workspace = os.path.realpath(workspace)
        self.home = os.path.realpath(os.path.expanduser("~"))
        # 白名单：Bash 允许的路径 (规范化为真实路径)
        self.allowed_base_paths = {
            os.path.realpath(os.path.expanduser(path))
            for path in settings.web_app_builder.security.allowed_directories
        }
        # 黑名单：敏感路径（所有工具共享，规范化为真实路径）
        self.sensitive_paths = {
            os.path.realpath(os.path.expanduser(path))
            for path in settings.web_app_builder.security.sensitive_paths
        }

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:  # type: ignore
        registry.add_callback(BeforeToolCallEvent, self.before_tool_call)

    def before_tool_call(self, event: BeforeToolCallEvent):
        # 空值检查：确保事件和工具信息完整
        if not event or not event.selected_tool or not event.selected_tool.tool_name:
            logger.warning("Invalid BeforeToolCallEvent: missing event or tool information")
            return

        if event.selected_tool.tool_name in ["file_read", "image_reader", "file_write", "editor", "shell"]:
            match event.selected_tool.tool_name:

                case "file_read":
                    path = cast(str, event.tool_use.get("input", {}).get("path"))
                    result = self.validate_file_path(path)

                    if not result.is_valid:
                        event.cancel_tool = result.error
                        return

                    # 替换为规范化后的路径
                    event.tool_use["input"]["path"] = result.normalized_path
                    logger.debug(f"✅ Path normalized: {path} -> {result.normalized_path}")

                case "image_reader":
                    path = cast(str, event.tool_use.get("input", {}).get("image_path"))
                    result = self.validate_file_path(path)

                    if not result.is_valid:
                        event.cancel_tool = result.error
                        return

                    # 替换为规范化后的路径
                    event.tool_use["input"]["image_path"] = result.normalized_path
                    logger.debug(f"✅ Image path normalized: {path} -> {result.normalized_path}")

                case "editor":
                    path = cast(str, event.tool_use.get("input", {}).get("path"))
                    result = self.validate_file_path(path)

                    if not result.is_valid:
                        event.cancel_tool = result.error
                        return

                    # 替换为规范化后的路径
                    event.tool_use["input"]["path"] = result.normalized_path
                    logger.debug(f"✅ Editor path normalized: {path} -> {result.normalized_path}")

                case "file_write":
                    path = cast(str, event.tool_use.get("input", {}).get("path"))
                    result = self.validate_file_path(path)

                    if not result.is_valid:
                        event.cancel_tool = result.error
                        return

                    # 替换为规范化后的路径
                    event.tool_use["input"]["path"] = result.normalized_path
                    logger.debug(f"✅ Write path normalized: {path} -> {result.normalized_path}")


                case "shell":
                    command = cast(
                        Union[str, List[Union[str, Dict[str, Any]]]],
                        event.tool_use.get("input", {}).get("command")
                    )
                    work_dir = cast(Optional[str], event.tool_use.get("input", {}).get("work_dir"))
                    result = self._validate_shell_command(command, work_dir)

                    if not result.is_valid:
                        event.cancel_tool = result.error
                        return

                    # 🔑 替换 work_dir 为规范化路径
                    if work_dir and result.normalized_path:
                        event.tool_use["input"]["work_dir"] = result.normalized_path
                        logger.debug(f"✅ Shell work_dir normalized: {work_dir} -> {result.normalized_path}")

                case _:
                    raise ValueError(f"Unknown tool: {event.selected_tool.tool_name}")

    def _validate_shell_command(
            self, commands: Union[str, List[Union[str, Dict[str, Any]]]],
            work_dir: Optional[str] = None
    ) -> ValidationResult:
        """验证 shell 命令的安全性

        支持三种格式：
        1. 单个命令字符串: "ls -la"
        2. 命令字符串数组: ["cd /path", "git status"]
        3. 命令对象数组: [{"command": "git clone repo", "work_dir": "/path"}]

        Returns:
            ValidationResult with:
            - is_valid: 命令是否安全
            - normalized_path: 规范化后的 work_dir（如果提供）
            - error: 错误信息（如果验证失败）
        """
        normalized_work_dir = None

        if work_dir:
            result = self.validate_file_path(work_dir, strict_mode=True)
            if not result.is_valid:
                return ValidationResult(
                    is_valid=False,
                    normalized_path=None,
                    error=f"Invalid work_dir: {result.error}"
                )
            cwd = result.normalized_path
            normalized_work_dir = result.normalized_path  # 🔑 保存规范化的 work_dir
        else:
            cwd = self.workspace

        # 格式 1: 单个命令字符串
        try:
            if isinstance(commands, str):
                # 使用 split_command 分割命令（处理 &&, ||, ; 等分隔符）
                split_commands = self.split_command(commands)

                # 验证所有分割后的命令
                is_valid, error = self.validate_commands(split_commands, cwd)
                return ValidationResult(
                    is_valid=is_valid,
                    normalized_path=normalized_work_dir,  # 🔑 返回规范化的 work_dir
                    error=error
                )

            # 格式 2 & 3: 数组格式
            elif isinstance(commands, list):
                # 格式 2: 命令字符串数组
                if all(isinstance(cmd, str) for cmd in commands):
                    all_commands = []
                    # 每个字符串可能包含多个命令（用 && 等连接）
                    for cmd_str in commands:
                        all_commands.extend(self.split_command(cmd_str))

                    # 验证所有命令
                    is_valid, error = self.validate_commands(all_commands, cwd)
                    return ValidationResult(
                        is_valid=is_valid,
                        normalized_path=None,
                        error=error
                    )

                # 格式 3: 命令对象数组
                elif all(isinstance(cmd, dict) for cmd in commands):
                    for cmd_obj in commands:
                        # 提取命令字符串
                        cmd_str = cmd_obj.get("command")
                        if not cmd_str:
                            continue

                        # 提取并验证 work_dir（如果存在）
                        obj_work_dir = cmd_obj.get("work_dir")
                        if obj_work_dir:
                            # 验证 work_dir 路径（严格模式）
                            result = self.validate_file_path(obj_work_dir, strict_mode=True)
                            if not result.is_valid:
                                return result
                            current_cwd = result.normalized_path
                        else:
                            current_cwd = cwd  # 使用传入的默认 work_dir

                        # 分割并验证命令（使用当前对象的 work_dir）
                        split_cmds = self.split_command(cmd_str)
                        is_valid, error = self.validate_commands(split_cmds, current_cwd)
                        if not is_valid:
                            return ValidationResult(
                                is_valid=is_valid,
                                normalized_path=None,
                                error=error
                            )
                    return ValidationResult(
                        is_valid=True,
                        normalized_path=None,
                        error=None
                    )
                else:
                    return ValidationResult(
                        is_valid=False,
                        normalized_path=None,
                        error="The command array cannot mix string and object types"
                    )
            else:
                return ValidationResult(
                    is_valid=False,
                    normalized_path=None,
                    error=f"Unsupported command format: {type(commands)}"
                )
        except PermissionError as e:
            logger.error(e)
            return ValidationResult(
                is_valid=False,
                normalized_path=None,
                error=f"{type(e).__name__}: {e}"
            )

    def expand_path_for_tilde(self, path: str) -> str:
        return re.sub(r'^~(?=/|$)', self.home, path)

    @staticmethod
    def is_banned_command(base_cmd: str) -> bool:
        if not base_cmd:
            return False

        return base_cmd.lower() in BANNED_COMMANDS

    def normalize_file_path(self, path: str) -> str:
        """规范化文件路径，解析符号链接防止绕过攻击

        🔒 安全修复：使用 realpath() 而非 normpath() + abspath()
        - realpath() 会解析所有符号链接，防止攻击者通过符号链接绕过敏感路径检查
        - 处理 TOCTOU 风险：虽然无法完全消除，但至少在检查时看到真实路径
        """
        expanded_path = self.expand_path_for_tilde(path)

        # macOS 截图文件名特殊处理（在路径解析前处理，避免干扰）
        if expanded_path.endswith(' AM.png'):
            expanded_path = expanded_path.replace(' AM.png', f'{chr(8239)}AM.png')
        elif expanded_path.endswith(' PM.png'):
            expanded_path = expanded_path.replace(' PM.png', f'{chr(8239)}PM.png')

        # 🔒 关键安全修复：使用 realpath 解析符号链接
        if os.path.isabs(expanded_path):
            # 绝对路径：直接解析
            try:
                absolute_path = os.path.realpath(expanded_path)
            except (OSError, ValueError):
                # realpath 可能失败（如路径不存在），降级到 normpath
                absolute_path = os.path.normpath(expanded_path)
        else:
            # 相对路径：相对于 workspace 解析
            try:
                absolute_path = os.path.realpath(os.path.join(self.workspace, expanded_path))
            except (OSError, ValueError):
                # 降级处理
                absolute_path = os.path.abspath(os.path.join(self.workspace, expanded_path))

        return absolute_path

    def validate_file_path(self, path: str, strict_mode: bool = False):
        """验证文件路径是否符合安全策略

        🔒 安全检查：
        1. 黑名单检查：禁止访问敏感路径（如 ~/.ssh, ~/.aws 等）
        2. 白名单检查（仅 strict_mode）：仅允许访问指定目录
        3. 路径遍历防护：防止 ../ 攻击
        4. 🪟 Windows 兼容：路径比较大小写不敏感
        """
        try:
            # 规范化路径（解析符号链接）
            absolute_path = self.normalize_file_path(path)

            # 🪟 Windows 兼容：统一转换为小写进行比较（Windows 路径不区分大小写）
            # Unix 系统上这不影响安全性，因为 realpath 已经规范化了路径
            is_windows = os.name == 'nt'
            compare_path = absolute_path.lower() if is_windows else absolute_path

            # 1. 黑名单检查：敏感路径（所有模式都检查）
            # 注意：self.sensitive_paths 已经在 __init__ 中使用 realpath 规范化
            for sensitive_path in self.sensitive_paths:
                # 🪟 Windows 兼容：统一转换为小写比较
                compare_sensitive = sensitive_path.lower() if is_windows else sensitive_path

                if compare_path == compare_sensitive or compare_path.startswith(compare_sensitive + os.sep):
                    logger.warning(f"🚫 Blocked access to sensitive path: {absolute_path}")
                    return ValidationResult(
                        is_valid=False,
                        normalized_path=absolute_path,
                        error=f'Access to sensitive directory is not allowed for security reasons'
                    )

            # 2. 白名单检查（仅严格模式）
            if strict_mode:
                is_in_allowed_path = False
                # 注意：self.allowed_base_paths 已经在 __init__ 中使用 realpath 规范化
                for base_path in self.allowed_base_paths:
                    # 检查是否是子路径
                    try:
                        rel_path = os.path.relpath(absolute_path, base_path)

                        # 检查是否需要向上遍历（路径遍历攻击防护）
                        # 只拒绝 '..' 或 '../xxx'，允许 '..config' 等合法文件名
                        if rel_path == '..' or rel_path.startswith('../'):
                            # 需要跳出基础目录，不允许
                            continue

                        # 在基础目录内或就是基础目录本身
                        is_in_allowed_path = True
                        break
                    except ValueError:
                        # 在不同的驱动器上（Windows）
                        continue

                if not is_in_allowed_path:
                    # 格式化允许路径列表（转换为字符串）
                    allowed_paths_str = ", ".join(str(p) for p in self.allowed_base_paths)
                    logger.warning(f"🚫 Blocked access outside allowed directories: {absolute_path}")
                    return ValidationResult(
                        is_valid=False,
                        normalized_path=absolute_path,
                        error=f'Path is outside allowed directories ({allowed_paths_str})'
                    )

            return ValidationResult(
                is_valid=True,
                normalized_path=absolute_path
            )
        except Exception as e:
            logger.error(f"❌ Error validating file path '{path}': {e}")
            return ValidationResult(
                is_valid=False,
                normalized_path=path,
                error=f'Path validation error: {str(e)}'
            )

    @staticmethod
    def parse_base_command(cmd: str) -> Optional[str]:
        """
        从命令字符串中提取基础命令名（防绕过版本）

        🔒 安全增强：
        - 处理绝对路径：/usr/bin/python3 -> python3
        - 处理相对路径：./python3 -> python3
        - 处理 env 调用：env python3 -> python3

        Args:
            cmd: 命令字符串

        Returns:
            基础命令名，如果解析失败返回 None
        """
        # Python 优雅的空值检查：利用 str.strip() 的返回值
        if not (cmd and cmd.strip()):
            return None

        try:
            # 使用 shlex 智能分割（处理引号）
            parts = shlex.split(cmd.strip())
            if not parts:
                return None

            base_cmd = parts[0]

            # 🔒 处理 env 命令：env python3 -> python3
            if base_cmd == 'env' and len(parts) > 1:
                # env 后面可能有环境变量设置，找到第一个不含 = 的参数
                for part in parts[1:]:
                    if '=' not in part:
                        base_cmd = part
                        break

            # 🔒 提取文件名（处理路径）
            # /usr/bin/python3 -> python3
            # ./python -> python
            # ../bin/node -> node
            base_cmd = os.path.basename(base_cmd)

            return base_cmd.lower() if base_cmd else None

        except (ValueError, AttributeError):
            # shlex 失败时降级到简单分割
            # AttributeError 处理 cmd 不是字符串的情况
            try:
                parts = cmd.strip().split()
                if not parts:
                    return None

                base_cmd = parts[0]

                # 处理 env 命令
                if base_cmd == 'env' and len(parts) > 1:
                    for part in parts[1:]:
                        if '=' not in part:
                            base_cmd = part
                            break

                # 提取文件名
                base_cmd = os.path.basename(base_cmd)
                return base_cmd.lower() if base_cmd else None

            except AttributeError:
                return None

    def validate_command_safety(self, commands: List[str]) -> Tuple[bool, Optional[str]]:
        """
        检查命令列表中是否包含禁用命令

        Args:
            commands: 命令字符串列表

        Returns:
            (is_valid, error_message) 元组

        """
        for cmd in commands:
            base_cmd = self.parse_base_command(cmd)
            if not base_cmd:
                continue

            # 先检查是否为禁用命令
            if self.is_banned_command(base_cmd):
                return False, f"Command '{base_cmd}' is not allowed for security reasons"

        return True, None

    def validate_cd_path(
            self,
            target_dir: str,
            cwd: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        检查 cd 命令的目标路径是否安全（使用 SecureFileService）

        Args:
            target_dir: cd 的目标路径
            cwd: 当前工作目录

        Returns:
            (is_valid, error_message) 元组
        """
        # 🔑 先展开 ~ 为 E2B home（在路径拼接前处理）
        expanded_dir = self.expand_path_for_tilde(target_dir)

        # 解析为绝对路径
        if os.path.isabs(expanded_dir):
            full_target_dir = expanded_dir
        else:
            full_target_dir = os.path.abspath(os.path.join(cwd, expanded_dir))

        # 🔑 使用 SecureFileService 进行验证（严格模式）
        result = self.validate_file_path(full_target_dir, strict_mode=True)

        if not result.is_valid:
            return False, result.error

        return True, None

    @staticmethod
    def extract_potential_paths(command: str) -> List[str]:
        """
        从 Bash 命令中提取可能的路径（增强版）

        🔒 安全增强：
        1. 分割命令为 tokens（使用 shlex 处理引号）
        2. 识别看起来像路径的 token
        3. 提取重定向符号后的路径
        4. 检测 heredoc 模式
        5. 检测进程替换模式（虽然被 split_command 阻止，但双重保护）

        Args:
            command: Bash 命令字符串

        Returns:
            可能的路径列表
        """
        potential_paths = []

        # 1. 使用 shlex 分割（处理引号）
        try:
            parts = shlex.split(command.strip())
        except ValueError:
            # 解析失败，降级到简单分割
            parts = command.strip().split()

        if not parts:
            return []

        # 2. 遍历所有 token，识别路径特征
        for i, part in enumerate(parts):
            # 跳过命令本身（第一个 token）
            if i == 0:
                continue

            # 跳过所有选项（短选项和长选项）
            # 短选项：-a, -rf, -la 等
            # 长选项：--verbose, --file=/path 等
            if part.startswith('-'):
                # 特殊情况：单独的 '-' 表示 stdin/stdout，不是选项
                if part != '-':
                    # 处理长选项中的路径（如 --file=/path）
                    if part.startswith('--') and '=' in part:
                        # 提取 = 后面的值作为可能的路径
                        _, potential_path = part.split('=', 1)
                        if potential_path:
                            potential_paths.append(potential_path)
                    continue

            # 识别路径特征
            looks_like_path = (
                    '/' in part or  # 绝对路径或包含目录分隔符
                    part.startswith('~') or  # 用户目录 ~/
                    part.startswith('.') or  # 相对路径 ./ ../ 或隐藏文件 .ssh
                    re.search(r'\.[a-zA-Z0-9]+$', part)  # 有文件扩展名 .txt .json
            )

            if looks_like_path:
                potential_paths.append(part)

        # 3. 特殊处理：重定向符号后的路径
        # > output.txt, >> log.txt, < input.txt
        redirect_patterns = [
            r'>\s*([^\s;|&]+)',  # > output
            r'>>\s*([^\s;|&]+)',  # >> output
            r'<\s*([^\s;|&<>]+)',  # < input (但排除 << heredoc)
        ]

        for pattern in redirect_patterns:
            matches = re.findall(pattern, command)
            potential_paths.extend(matches)

        # 4. 🔒 检测 heredoc 模式（cat <<EOF > file）
        # 虽然 split_command 会阻止 $()，但这里提供额外防护
        heredoc_pattern = r'<<\s*(\w+)'
        if re.search(heredoc_pattern, command):
            # heredoc 通常不涉及文件路径，但要警惕后面的重定向
            pass  # 已被上面的重定向检测覆盖

        # 5. 🔒 检测进程替换模式 <(cmd) 和 >(cmd)
        # 这些在 split_command 中已被阻止，这里只是记录
        process_substitution = re.findall(r'[<>]\([^)]+\)', command)
        if process_substitution:
            logger.warning(f"⚠️ Detected process substitution (should be blocked): {process_substitution}")

        # 去重
        return list(set(potential_paths))

    def validate_command_paths(self, command: str, cwd: str) -> Tuple[bool, Optional[str]]:
        """
        验证命令中的所有路径参数（复用 validate_file_path）

        Args:
            command: Bash 命令字符串
            cwd: 当前工作目录

        Returns:
            (is_valid, error_message) 元组
        """
        # 提取可能的路径
        potential_paths = self.extract_potential_paths(command)

        # 对每个路径验证（轻量模式，只检查敏感路径黑名单）
        for path in potential_paths:
            # 规范化为绝对路径
            try:
                if os.path.isabs(path):
                    full_path = path
                else:
                    expanded = self.expand_path_for_tilde(path)
                    full_path = os.path.abspath(os.path.join(cwd, expanded))

                # 🔑 复用 validate_file_path（轻量模式，只检查敏感路径）
                result = self.validate_file_path(full_path, strict_mode=False)

                if not result.is_valid:
                    return False, f"Command accesses sensitive path '{path}': {result.error}"

            except Exception as e:
                logger.error(f"{type(e).__name__}: {e}")
                # 路径处理失败，跳过（避免误杀）
                continue

        return True, None

    def validate_commands(
            self,
            commands: List[str],
            cwd: str
    ) -> Tuple[bool, Optional[str]]:
        """
        验证命令的完整逻辑（组合函数）


        增强：
        1. 检查所有命令中的路径参数，防止通过 Bash 绕过文件工具的安全检查
        2. 追踪 cd 命令导致的工作目录变化，正确验证命令链

        Args:
            commands: 分割后的命令列表
            cwd: 初始工作目录

        Returns:
            (is_valid, error_message) 元组
        """
        # 1. 检查禁用命令
        is_valid, error = self.validate_command_safety(commands)
        if not is_valid:
            return False, error

        # 🔑 追踪当前工作目录（会随 cd 命令更新）
        current_cwd = cwd

        # 2. 检查所有命令的路径参数
        for cmd in commands:
            # 解析命令获取基础命令名
            try:
                parts = shlex.split(cmd.strip())
            except ValueError:
                # 解析失败时降级到简单分割
                parts = cmd.strip().split()

            if not parts:
                continue

            base_cmd = parts[0].lower()

            # 2.1 检查 cd 命令（严格模式：白名单 + 黑名单）
            if base_cmd == 'cd':
                # 安全检查：cd 命令必须有目标路径
                if len(parts) < 2:
                    return False, "cd command requires a target directory"

                target_dir = parts[1]
                # 安全检查：防止空路径
                if not target_dir or not target_dir.strip():
                    return False, "cd target directory cannot be empty"

                # 🔑 使用当前追踪的 cwd 来验证
                is_valid, error = self.validate_cd_path(
                    target_dir,
                    current_cwd  # ← 使用动态更新的 cwd
                )
                if not is_valid:
                    return False, error

                # 🔑 更新 current_cwd（模拟 cd 的效果）
                expanded_dir = self.expand_path_for_tilde(target_dir)
                if os.path.isabs(expanded_dir):
                    new_cwd = expanded_dir
                else:
                    new_cwd = os.path.abspath(os.path.join(current_cwd, expanded_dir))

                # 验证并规范化新 cwd（确保路径安全且获得真实路径）
                result = self.validate_file_path(new_cwd, strict_mode=True)
                if result.is_valid:
                    current_cwd = result.normalized_path
                    logger.debug(f"📂 CWD updated by cd: {current_cwd}")
                else:
                    # 理论上不应该到这里，因为 validate_cd_path 已经验证过
                    return False, f"Invalid cd target: {result.error}"

            # 2.2 🔑 检查所有命令的路径参数（轻量模式：仅黑名单）
            # 防止用 cat/echo/rm 等绕过文件工具的安全检查
            # 使用更新后的 current_cwd
            is_valid, error = self.validate_command_paths(cmd, current_cwd)
            if not is_valid:
                return False, error

        return True, None

    def split_command(self, command: str) -> List[str]:
        """
        分割命令字符串为独立的命令列表

        正确处理：
        - 引号（单引号、双引号）
        - 转义字符
        - Shell 变量（$VAR, ${VAR}）
        - Glob 模式（*.txt, file?.log）
        - 注释（# comment）
        - 命令分隔符（&&, ||, ;）

        使用 Python shlex 库实现类似 shell-quote 的功能

        Args:
            command: 命令字符串

        Returns:
            分割后的命令列表

        Examples:
        """

        if not command.strip():
            return []

        # 🔒 Step 0: 预检查危险模式
        dangerous_patterns = [
            r'`[^`]*`',  # 反引号命令替换
            r'\$\([^)]*\)',  # $() 命令替换
            r'[\r\n]',  # 换行符注入
            r'[\u202a-\u202e]',  # Unicode 双向文本控制字符
            r'\${[^}]*}',  # 变量替换（可能包含命令）
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                raise PermissionError(f"Command contains dangerous pattern: {pattern}")

        # Step 1: 处理注释
        # 移除 # 后面的内容（但引号内的 # 不算注释）
        cleaned_command = self._remove_comments(command)

        # Step 2: 找出所有分隔符的位置（考虑引号）
        separator_positions = self._find_separators(cleaned_command)

        # Step 3: 根据分隔符分割命令（同时规范化空格）
        if not separator_positions:
            # 没有分隔符，整个是一个命令
            cmd = cleaned_command.strip()
            if cmd:
                # 直接规范化并返回
                return [self._normalize_spaces(cmd)]
            return []

        # Step 4: 分割并收集命令（一遍处理，同时规范化）
        commands = []
        start = 0

        for sep_pos, sep_len in separator_positions:
            cmd = cleaned_command[start:sep_pos].strip()
            if cmd:
                # 分割时就规范化空格
                commands.append(self._normalize_spaces(cmd))
            start = sep_pos + sep_len

        # 添加最后一个命令
        last_cmd = cleaned_command[start:].strip()
        if last_cmd:
            # 分割时就规范化空格
            commands.append(self._normalize_spaces(last_cmd))

        return commands

    @staticmethod
    def _remove_comments(command: str) -> str:
        """
        移除命令中的注释（# 后的内容）
        但保留引号内的 #
        """
        # 使用 shlex 解析来保留引号内容
        try:
            # shlex 可以正确处理引号和转义
            lexer = shlex.shlex(command, posix=True)
            lexer.commenters = '#'  # 设置注释符
            lexer.whitespace_split = False

            # 收集所有 token 直到遇到注释
            tokens = []
            for token in lexer:
                tokens.append(token)

            # 重组命令（保留原始空格结构）
            # 由于 shlex 会改变空格，我们需要更精细的处理
            # 这里使用简单的状态机来处理
            result = []
            in_quote = False
            quote_char = None
            escaped = False

            for i, char in enumerate(command):
                if escaped:
                    result.append(char)
                    escaped = False
                    continue

                if char == '\\':
                    result.append(char)
                    escaped = True
                    continue

                if char in ('"', "'") and not in_quote:
                    result.append(char)
                    in_quote = True
                    quote_char = char
                elif char == quote_char and in_quote:
                    result.append(char)
                    in_quote = False
                    quote_char = None
                elif char == '#' and not in_quote:
                    # 找到注释，停止
                    break
                else:
                    result.append(char)

            return ''.join(result)
        except (ValueError, SyntaxError):
            # 如果解析失败，返回原始命令
            return command

    @staticmethod
    def _find_separators(command: str) -> List[tuple]:
        """
        找出命令中所有分隔符的位置
        返回 [(position, length)] 列表

        处理 &&, ||, ; 分隔符，考虑引号和转义
        """
        separators = []
        i = 0
        length = len(command)

        # 状态追踪
        in_single_quote = False
        in_double_quote = False
        escaped = False

        while i < length:
            char = command[i]

            # 处理转义
            if escaped:
                escaped = False
                i += 1
                continue

            if char == '\\':
                escaped = True
                i += 1
                continue

            # 处理引号
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                i += 1
                continue
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                i += 1
                continue

            # 只在引号外检查分隔符
            if not in_single_quote and not in_double_quote:
                if char == ';':
                    separators.append((i, 1))
                    i += 1
                elif i + 1 < length:
                    two_char = command[i:i + 2]
                    if two_char == '&&' or two_char == '||':
                        separators.append((i, 2))
                        i += 2
                    else:
                        i += 1
                else:
                    i += 1
            else:
                i += 1

        return separators

    @staticmethod
    def _normalize_spaces(cmd: str) -> str:
        """
        规范化命令中的空格
        但保留引号内的空格不变
        """
        result = []
        in_single_quote = False
        in_double_quote = False
        escaped = False
        last_was_space = False

        for char in cmd:
            # 处理转义
            if escaped:
                result.append(char)
                escaped = False
                last_was_space = False
                continue

            if char == '\\':
                result.append(char)
                escaped = True
                last_was_space = False
                continue

            # 处理引号状态
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                result.append(char)
                last_was_space = False
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                result.append(char)
                last_was_space = False
            elif in_single_quote or in_double_quote:
                # 在引号内，保留所有字符（包括空格）
                result.append(char)
                last_was_space = False
            elif char in ' \t':
                # 在引号外的空白符
                if not last_was_space:
                    result.append(' ')  # 规范化为单个空格
                    last_was_space = True
            else:
                # 普通字符
                result.append(char)
                last_was_space = False

        return ''.join(result).strip()
