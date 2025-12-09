from typing import Optional, Type

from openai import BaseModel
from strands import Agent
from strands.agent import ConversationManager
from strands.hooks import HookProvider
from strands.session import SessionManager

from hatchify.common.domain.entity.agent_card import AgentCard
from hatchify.core.factory.llm_factory import create_llm_by_agent_card
from hatchify.core.manager.tool_manager import tool_factory


def create_agent_by_agent_card(
        agent_card: AgentCard,
        structured_output_model: Optional[Type[BaseModel]] = None,
        hooks: Optional[list[HookProvider]] = None,
        conversation_manager: Optional[ConversationManager] = None,
        session_manager: Optional[SessionManager] = None,
):
    model = create_llm_by_agent_card(agent_card)
    tools = [tool_factory.get_tool(tool) for tool in agent_card.tools]
    return Agent(
        model=model,
        tools=tools,
        system_prompt=agent_card.instruction,
        structured_output_model=structured_output_model,
        name=agent_card.name,
        description=agent_card.description,
        hooks=hooks,
        conversation_manager=conversation_manager,
        session_manager=session_manager,
    )
