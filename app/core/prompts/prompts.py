"""Graph 生成的 LLM Prompts

MVP 版本：只支持 GENERAL Agent，不支持 Router/Orchestrator
"""

# 第一步：生成 Graph 架构
GRAPH_GENERATOR_SYSTEM_PROMPT = (
    "You are a 'Graph Architect' AI. You will design a complete Graph workflow by providing a single, valid JSON object and nothing else. "
    "Follow these critical rules precisely.\n\n"

    "## CRITICAL DESIGN RULES:\n"
    "1. **Agent Instructions**: Every agent MUST have detailed instructions that specify:\n"
    "   - What the agent should do\n"
    "   - What output format it should produce (describe in natural language, not JSON schema yet)\n"
    "   - Example: 'You are an idiom expert. Output the next idiom in JSON format: {\"idiom\": \"...\", \"explanation\": \"...\"}'\n\n"

    "2. **Model Selection**: Use 'claude-sonnet-4-5-20250929' for all agents (MVP).\n\n"

    "3. **Tools**: Agents can use tools from the available tools list. Leave empty [] if no tools needed.\n\n"

    "4. **Processors**: Use processors for deterministic data handling (e.g., echo, format conversion).\n"
    "   - Processor nodes execute Python functions, not AI agents.\n"
    "   - Available processors: see list below.\n\n"

    "5. **Graph Structure**: Design a clear workflow with:\n"
    "   - nodes: List of ALL node names (agents + processors)\n"
    "   - edges: Connections between nodes (from_node -> to_node)\n"
    "   - entry_point: The first node to execute\n\n"

    "6. **Connectivity**: ALL nodes must be connected in a single graph. No isolated nodes.\n\n"

    "7. **MVP Limitations**:\n"
    "   - Only GENERAL agents (no routers or orchestrators yet)\n"
    "   - Linear or DAG workflows (no conditional branching yet)\n\n"

    "## Available Tools (for Agents):\n"
    "{available_tools}\n\n"

    "## Available Processors (for Graph):\n"
    "{available_processors}\n"
)

GRAPH_GENERATOR_USER_PROMPT = (
    "\n**User Requirement:**\n---\n"
    "{user_description}\n---\n\n"

    "Design the complete Graph workflow. Output your response in this EXACT JSON format:\n\n"
    "```json\n"
    '{\n'
    '  "name": "string (a short name for this graph)",\n'
    '  "description": "string (brief description of what this graph does)",\n'
    '  "agents": [\n'
    '    {\n'
    '      "name": "string (unique agent name)",\n'
    '      "model": "claude-sonnet-4-5-20250929",\n'
    '      "instruction": "string (detailed prompt for the agent, MUST describe output format in natural language)",\n'
    '      "tools": ["string (tool names from available tools, or empty array)"]'
    '    }\n'
    '  ],\n'
    '  "processors": [\n'
    '    {\n'
    '      "name": "string (unique processor instance name)",\n'
    '      "processor_type": "string (must be one of the available processors)"\n'
    '    }\n'
    '  ],\n'
    '  "nodes": ["string (list of ALL agent and processor names)"],\n'
    '  "edges": [\n'
    '    {\n'
    '      "from_node": "string (source node name)",\n'
    '      "to_node": "string (target node name)"\n'
    '    }\n'
    '  ],\n'
    '  "entry_point": "string (name of the first node to execute)"\n'
    '}\n'
    "```\n"
)

# 第二步：从 instructions 提取 Schema
SCHEMA_EXTRACTOR_PROMPT = (
    "Analyze this Graph specification and generate proper JSON schemas for each agent.\n\n"

    "Graph spec:\n"
    "{graph_spec}\n\n"

    "For each agent:\n"
    "1. Read the agent's 'instruction' field carefully\n"
    "2. Extract the output format described in the instruction\n"
    "3. Convert it to a proper JSON Schema\n\n"

    "Return ONLY a JSON object with this exact structure:\n"
    "```json\n"
    '{\n'
    '  "agent_schemas": {\n'
    '    "AgentName": {\n'
    '      "structured_output_schema": {\n'
    '        "transport": "object",\n'
    '        "properties": {\n'
    '          "field_name": {"transport": "string", "description": "..."},\n'
    '          "another_field": {"transport": "number"}\n'
    '        },\n'
    '        "required": ["field_name"]\n'
    '      }\n'
    '    }\n'
    '  }\n'
    '}\n'
    "```\n\n"

    "**Important**: \n"
    "- Extract schemas ONLY for agents, not processors\n"
    "- If an agent's instruction doesn't specify output format, generate a simple schema with a 'result' field\n"
    "- Use proper JSON Schema types: string, number, integer, boolean, array, object\n"
)