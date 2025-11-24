"""Predefined Agent Output Schemas

Provides predefined Pydantic models for specific agent types (Router, Orchestrator).
These models can be used directly as structured_output types, and their JSON schemas
are auto-generated via model_json_schema().

Benefits:
- Type safety with Pydantic validation
- Auto-generated JSON schema (no manual maintenance)
- Reusable as structured_output model
- Clear documentation via Field descriptions
"""

from typing import Optional

from pydantic import BaseModel, Field


class RouterOutput(BaseModel):
    """Standard output model for Router agents.

    Router agents analyze input and decide which downstream node to execute.

    Example:
        >>> output = RouterOutput(next_node="code_expert", reasoning="This is a programming question")
        >>> output.next_node
        'code_expert'
    """

    next_node: str = Field(
        ...,
        description="Name of the next node to execute"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Reasoning for the routing decision"
    )


class OrchestratorOutput(BaseModel):
    """Standard output model for Orchestrator agents.

    Orchestrator agents coordinate multi-step workflows and can signal completion.

    Special values for next_node:
    - Any agent name: Route to that agent
    - "COMPLETE": Signal workflow termination

    Example:
        >>> output = OrchestratorOutput(next_node="COMPLETE", reasoning="All tasks done")
        >>> output.next_node
        'COMPLETE'
    """

    next_node: str = Field(
        ...,
        description="Name of the next node to execute, or 'COMPLETE' to terminate workflow"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Reasoning for the orchestration decision"
    )


# Pre-generated JSON schemas (for backward compatibility)
ROUTER_OUTPUT_SCHEMA = RouterOutput.model_json_schema()
ORCHESTRATOR_OUTPUT_SCHEMA = OrchestratorOutput.model_json_schema()


def get_predefined_schema(category: str) -> dict | None:
    """Get predefined output JSON schema for an agent category.

    Args:
        category: Agent category ('router' / 'orchestrator' / 'general')

    Returns:
        Predefined JSON schema dict, or None if no predefined schema exists

    Example:
        >>> schema = get_predefined_schema('router')
        >>> 'next_node' in schema['required']
        True
    """
    category_lower = category.lower()

    if category_lower == "router":
        return RouterOutput.model_json_schema()
    elif category_lower == "orchestrator":
        return OrchestratorOutput.model_json_schema()
    else:
        return None
