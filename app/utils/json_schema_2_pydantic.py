from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel
from pydantic import Field
from pydantic import create_model


def jsonschema_to_pydantic(
        schema: dict, definitions: dict = None
) -> Type[BaseModel]:
    title = schema.get("title", "DynamicModel")
    description = schema.get("description", None)

    if definitions is None:
        if "$defs" in schema:
            definitions = schema["$defs"]
        elif "definitions" in schema:
            definitions = schema["definitions"]
        else:
            definitions = {}

    def convert_type(_prop: dict) -> Any:
        if "$ref" in _prop:
            ref_path = _prop["$ref"].split("/")
            ref = definitions[ref_path[-1]]
            return jsonschema_to_pydantic(ref, definitions)

        if "type" in _prop:
            type_mapping = {
                "string": str,
                "number": float,
                "integer": int,
                "boolean": bool,
                "array": List,
                "object": Dict[str, Any],
                "null": None,
            }

            type_ = _prop["type"]

            if type_ == "array":
                return List[convert_type(_prop.get("items", {}))]
            elif type_ == "object":
                if "properties" in _prop:
                    return jsonschema_to_pydantic(_prop, definitions)
                else:
                    return Dict[str, Any]
            else:
                return type_mapping.get(type_, Any)

        elif "allOf" in _prop:
            combined_fields = {}
            for sub_schema in _prop["allOf"]:
                _model = jsonschema_to_pydantic(sub_schema, definitions)
                combined_fields.update(_model.__annotations__)
            return create_model("CombinedModel", **combined_fields)

        elif "anyOf" in _prop:
            union_types = tuple(convert_type(sub_schema) for sub_schema in _prop["anyOf"])
            return Union[union_types]
        elif _prop == {} or "type" not in _prop:
            return Any
        else:
            raise ValueError(f"Unsupported schema: {_prop}")

    fields = {}
    required_fields = schema.get("required", [])

    for name, prop in schema.get("properties", {}).items():
        pydantic_type = convert_type(prop)
        field_kwargs = {}
        if "default" in prop:
            field_kwargs["default"] = prop["default"]
        if name not in required_fields:
            pydantic_type = Optional[pydantic_type]
            if "default" not in field_kwargs:
                field_kwargs["default"] = None
        if "description" in prop:
            field_kwargs["description"] = prop["description"]

        fields[name] = (pydantic_type, Field(**field_kwargs))

    model = create_model(title, **fields)
    if description:
        model.__doc__ = description
    return model
