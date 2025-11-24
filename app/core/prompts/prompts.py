"""Graph 生成的 LLM Prompts

支持 GENERAL Agent、Router 和 Orchestrator
"""

# 第一步：生成 Graph 架构
GRAPH_GENERATOR_SYSTEM_PROMPT = (
    "You are a 'Graph Architect' AI. You will design a complete Graph workflow by providing a single, valid JSON object and nothing else. "
    "Follow these critical rules precisely.\n\n"

    "## CRITICAL DESIGN RULES:\n"
    "1. **Agent Instructions**: Every agent MUST have detailed instructions that specify:\n"
    "   - What the agent should do\n"
    "   - What output format it should produce (describe in natural language, not JSON schema yet)\n"
    "   - Example: 'You are an idiom expert. Output the next idiom in JSON format: {{\"idiom\": \"...\", \"explanation\": \"...\"}}'\n\n"

    "2. **Model Selection**: Choose from the available models list below.\n\n"

    "3. **Tools**: Agents can use tools from the available tools list. Leave empty [] if no tools needed.\n\n"

    "4. **Functions**: Use functions for deterministic data handling (e.g., echo, format conversion).\n"
    "   - Function nodes execute Python functions, not AI agents.\n"
    "   - Each function has a defined Input Schema and Output Schema (see list below).\n"
    "   - **CRITICAL**: When an Agent connects to a Function (Agent -> Function), the Agent's output MUST match the Function's Input Schema exactly.\n"
    "   - Example: If function 'echo_function' has Input Schema {{'text': 'string'}}, the upstream Agent MUST output {{'text': '...'}}\n\n"

    "5. **Agent Categories**: Agents can be one of three types:\n"
    "   - **GENERAL** (default): Regular agents that perform specific tasks\n"
    "   - **ROUTER**: Conditional routing agents that decide which path to take based on input\n"
    "   - **ORCHESTRATOR**: Central coordinator that manages workflow execution\n\n"

    "6. **Router Agent Rules**:\n"
    "   - Use when you need conditional branching (if-else logic)\n"
    "   - Output schema is predefined: {{\"next_node\": \"target_name\", \"reasoning\": \"...\" (optional)}}\n"
    "   - Must have 2+ outgoing edges (different paths to route to)\n"
    "   - Instructions MUST list all possible routing targets with routing conditions\n"
    "   - Example instruction: 'Analyze content quality. Route to \"high_quality\" if score >= 80, \"medium_quality\" if 50-79, \"low_quality\" if < 50. Output your routing decision with reasoning.'\n\n"

    "7. **Orchestrator Agent Rules**:\n"
    "   - Use when you need iterative coordination (while loop logic)\n"
    "   - Output schema is predefined: {{\"next_node\": \"target_name\" | \"COMPLETE\", \"reasoning\": \"...\" (optional)}}\n"
    "   - Should be the entry_point of the graph\n"
    "   - Other agents return to Orchestrator after completion (Hub-and-Spoke pattern)\n"
    "   - Can output {{\"next_node\": \"COMPLETE\"}} to terminate the workflow\n"
    "   - Instructions MUST list all available agents and explain coordination logic\n"
    "   - Example instruction: 'Coordinate research workflow. Available agents: DataCollector, Analyzer, Reporter. First collect data, then analyze, then report. Output {{\"next_node\": \"COMPLETE\"}} when done.'\n\n"

    "8. **Graph Structure**: Design a clear workflow with:\n"
    "   - nodes: List of ALL node names (agents + functions)\n"
    "   - edges: Connections between nodes (from_node -> to_node)\n"
    "   - entry_point: The first node to execute\n\n"

    "9. **Connectivity**: ALL nodes must be connected in a single graph. No isolated nodes.\n\n"

    "10. **Router/Orchestrator Output Schema**:\n"
    "   - Router/Orchestrator agents MUST have 'next_node' as a required field in their output\n"
    "   - This will be automatically enforced during schema extraction\n\n"

    "## Available Models:\n"
    "{available_models}\n\n"

    "## Available Tools (for Agents):\n"
    "{available_tools}\n\n"

    "## Available Functions (for Graph):\n"
    "{available_functions}\n"
)

GRAPH_GENERATOR_USER_PROMPT = (
    "\n**User Requirement:**\n---\n"
    "{user_description}\n---\n\n"

    "Design the complete Graph workflow. Output your response in this EXACT JSON format:\n\n"
    "```json\n"
    '{{\n'
    '  "name": "string (a short name for this graph)",\n'
    '  "description": "string (brief description of what this graph does)",\n'
    '  "agents": [\n'
    '    {{\n'
    '      "name": "string (unique agent name)",\n'
    '      "model": "string (model id from available models)",\n'
    '      "instruction": "string (detailed prompt for the agent, MUST describe output format in natural language)",\n'
    '      "category": "string (optional: \\"general\\", \\"router\\", or \\"orchestrator\\". Default is \\"general\\")",\n'
    '      "tools": ["string (tool names from available tools, or empty array)"]'
    '    }}\n'
    '  ],\n'
    '  "functions": [\n'
    '    {{\n'
    '      "name": "string (unique function instance name)",\n'
    '      "function_ref": "string (must be one of the available functions)"\n'
    '    }}\n'
    '  ],\n'
    '  "nodes": ["string (list of ALL agent and function names)"],\n'
    '  "edges": [\n'
    '    {{\n'
    '      "from_node": "string (source node name)",\n'
    '      "to_node": "string (target node name)"\n'
    '    }}\n'
    '  ],\n'
    '  "entry_point": "string (name of the first node to execute)"\n'
    '}}\n'
    "```\n\n"
    "**CRITICAL**: For Router/Orchestrator agents:\n"
    "- Set category to \"router\" or \"orchestrator\"\n"
    "- Instructions MUST specify all routing targets\n"
    "- Instructions MUST explain output format with 'next_node' field\n"
)

# 第二步：从 instructions 提取 Schema
SCHEMA_EXTRACTOR_PROMPT = (
    "\n**Graph Specification:**\n---\n"
    "{graph_spec}\n---\n\n"

    "Analyze the above Graph specification and generate proper JSON schemas for each agent.\n\n"

    "## Instructions:\n"
    "For each agent in the spec:\n"
    "1. Read the agent's 'instruction' field carefully\n"
    "2. Extract the output format described in the instruction\n"
    "3. Convert it to a proper JSON Schema\n"
    "4. **CRITICAL**: If the agent has category='router' or 'orchestrator', the schema MUST include 'next_node' as a required string field\n\n"

    "## Requirements:\n"
    "- Extract schemas ONLY for agents, not functions\n"
    "- If an agent's instruction doesn't specify output format, generate a simple schema with a 'result' field\n"
    "- Use proper JSON Schema types: string, number, integer, boolean, array, object\n"
    "- **Router/Orchestrator agents**: MUST have 'next_node' field with type 'string' in required array\n\n"

    "Output your response in this EXACT format:\n\n"
    "```json\n"
    '{{\n'
    '  "agent_schemas": [\n'
    '    {{\n'
    '      "agent_name": "string (must match agent name from the spec)",\n'
    '      "structured_output_schema": {{\n'
    '        "type": "object",\n'
    '        "properties": {{\n'
    '          "next_node": {{\n'
    '            "type": "string",\n'
    '            "description": "Name of the next node to execute (REQUIRED for router/orchestrator)"\n'
    '          }},\n'
    '          "field_name": {{\n'
    '            "type": "string | number | integer | boolean | array | object",\n'
    '            "description": "string (optional field description)",\n'
    '            "items": {{...}} (only if type is array),\n'
    '            "properties": {{...}} (only if type is object)\n'
    '          }}\n'
    '        }},\n'
    '        "required": ["next_node", "field_name"]\n'
    '      }}\n'
    '    }}\n'
    '  ]\n'
    '}}\n'
    "```\n\n"
    "**Important Notes**:\n"
    "- Each property in `properties` must have at least a `type` field\n"
    "- The `properties` object must contain at least one field (cannot be empty)\n"
    "- Use `description` to explain what each field represents\n"
    "- Only include `items` if the type is 'array', and `properties` if the type is 'object'\n"
    "- **CRITICAL for Router/Orchestrator**: 'next_node' MUST be in the 'required' array\n"
)