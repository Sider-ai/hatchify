"""Webhook 工具模块

提供从 input_schema 推断 webhook_spec 的工具函数。

设计理念：
- input_schema 是唯一的数据源（Single Source of Truth）
- webhook_spec 在运行时实时推断，不存储
- 推断规则简单明确：有 format: 'binary' → multipart/form-data，否则 → application/json
"""

from typing import Dict, Any, List, Literal

from app.common.domain.entity.webhook_spec import WebhookSpec


def infer_webhook_spec_from_schema(input_schema: Dict[str, Any] | None) -> WebhookSpec:
    """从 input_schema 实时推断 webhook_spec

    推断规则：
    1. 如果 input_schema 为空 → 默认 application/json
    2. 遍历所有字段：
       - format: 'binary' → file_fields
       - 其他 → data_fields
    3. 有 file_fields → input_type = 'multipart/form-data'
       无 file_fields → input_type = 'application/json'

    Args:
        input_schema: JSON Schema 定义（可能为 None）

    Returns:
        WebhookSpec: 推断出的 webhook 规范

    Examples:
        >>> # 示例 1: 纯 JSON（无文件）
        >>> schema = {
        ...     "type": "object",
        ...     "properties": {
        ...         "text": {"type": "string"},
        ...         "max_length": {"type": "integer"}
        ...     }
        ... }
        >>> spec = infer_webhook_spec_from_schema(schema)
        >>> spec.input_type
        'application/json'
        >>> spec.file_fields
        []
        >>> spec.data_fields
        ['text', 'max_length']

        >>> # 示例 2: Multipart（有文件）
        >>> schema = {
        ...     "type": "object",
        ...     "properties": {
        ...         "document": {"type": "string", "format": "binary"},
        ...         "analysis_type": {"type": "string"}
        ...     }
        ... }
        >>> spec = infer_webhook_spec_from_schema(schema)
        >>> spec.input_type
        'multipart/form-data'
        >>> spec.file_fields
        ['document']
        >>> spec.data_fields
        ['analysis_type']

        >>> # 示例 3: 空 schema
        >>> spec = infer_webhook_spec_from_schema(None)
        >>> spec.input_type
        'application/json'
    """
    # 默认值：空输入或没有字段 → application/json
    if not input_schema:
        return WebhookSpec(
            input_type="application/json"
        )

    # 提取 properties
    properties = input_schema.get("properties", {})
    if not properties:
        return WebhookSpec(
            input_type="application/json"
        )

    # 遍历字段，分类为 file_fields 或 data_fields
    file_fields: List[str] = []
    data_fields: List[str] = []

    for field_name, field_schema in properties.items():
        if field_schema.get("format") == "binary":
            file_fields.append(field_name)
        else:
            data_fields.append(field_name)

    # 根据是否有文件字段决定 input_type
    input_type: Literal[
        "application/json", "multipart/form-data"] = "multipart/form-data" if file_fields else "application/json"

    return WebhookSpec(
        input_type=input_type,
        input_schema=input_schema,
        file_fields=file_fields,
        data_fields=data_fields,
    )
