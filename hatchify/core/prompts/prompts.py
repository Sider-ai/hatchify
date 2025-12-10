from textwrap import dedent

GRAPH_NAME_SYSTEM_PROMPT = dedent(
    "You are a helpful assistant that generates concise, descriptive names for workflows. "
    "Generate a name that is 2-5 words long, descriptive, and easy to understand. "
    "Also craft a brief description (1-2 sentences) that explains what the workflow does. "
    "Always respond with JSON: {\"name\": \"...\", \"description\": \"...\"}."
)

GRAPH_NAME_USER_PROMPT = dedent(
    "Based on this workflow description, generate a short name (2-5 words) and a concise description:\n\n"
    "{genesis_prompt}\n\n"
    "Respond ONLY with JSON using keys \"name\" and \"description\"."
)

# 第一步：生成 Graph 架构
GRAPH_GENERATOR_SYSTEM_PROMPT = dedent(
    "You are a 'Graph Architect' AI. You will design a complete Graph workflow by providing a single, valid JSON object and nothing else. "
    "The system can contain both AI-powered 'agents' and deterministic 'functions' for data handling. Follow these critical rules precisely.\n\n"

    "## CRITICAL DESIGN RULES:\n"

    "1. **Input Schema First**: Always start by analyzing the workflow's input requirements.\n"
    "   - Does the task require file uploads (PDF, images, audio, video, documents)?\n"
    "   - If YES → Mark those fields with `\"format\": \"data-url\"` in input_schema (system will use multipart/form-data)\n"
    "   - If NO → Use standard JSON Schema types (system will use application/json)\n"
    "   - **CRITICAL**: Keywords like 'upload', 'file', 'PDF', 'image', 'document', 'audio', 'video' indicate file inputs\n\n"

    "2. **Agent Instructions**: Every agent MUST have detailed instructions that specify:\n"
    "   - What the agent should do\n"
    "   - What output format it should produce (describe in natural language)\n"
    "   - Enumerate the JSON fields you will emit so schemas can be extracted and matched to downstream rules/functions\n"
    "   - Example: 'You are an idiom expert. Output the next idiom in JSON format: {{\"idiom\": \"...\", \"explanation\": \"...\"}}'\n\n"

    "3. **Model Selection**: Choose from the available models list below.\n\n"

    "4. **Tools**: Agents can use tools from the available tools list. Leave empty [] if no tools needed.\n\n"

    "5. **Functions**: Use functions for deterministic data handling (e.g., echo, format conversion).\n"
    "   - Function nodes execute Python functions, not AI agents.\n"
    "   - Each function has a defined Input Schema and Output Schema (see list below).\n"
    "   - **CRITICAL**: When an Agent connects to a Function (Agent -> Function), the Agent's output MUST match the Function's Input Schema exactly.\n\n"

    "6. **Orchestration Patterns**: Choose the pattern that best fits the task requirements. Prioritize simplicity, but don't force linear workflows when parallelism or conditional logic would be more efficient or appropriate.\n"
    "   - **Sequential**: When each step depends on the previous step's output (e.g., retrieve data → process data → format results)\n"
    "   - **Parallel**: When multiple independent tasks can run simultaneously to save time (e.g., fetch from 3 different APIs, analyze multiple documents, gather data from separate sources). Use this when tasks don't depend on each other.\n"
    "   - **Router Agent**: When the workflow needs conditional branching based on data or validation (e.g., quality check that either approves or rejects, classification that routes to different handlers)\n"
    "   - **Orchestrator Agent**: When the user explicitly requests a coordinator OR when complex runtime decision-making is needed to manage multiple specialized agents dynamically\n"
    "   - **Loop Patterns with Conditional Exit**: If the workflow requires iteration until a condition is met (e.g., Agent-A produces output, Agent-B evaluates it, and either approves to proceed to Agent-C or sends back to Agent-A for revision), make the evaluator agent (Agent-B) a ROUTER AGENT with category 'router'. The router must output {{\"next_node\": \"AgentName\"}} to conditionally choose between looping back or proceeding forward.\n"
    "   - **Hybrid**: When appropriate (e.g., parallel fetch → sequential processing, or sequential steps with conditional branches)\n\n"

    "7. **Router Agent Rules**:\n"
    "   - Use when you need conditional branching (if-else logic)\n"
    "   - Set category to \"router\"\n"
    "   - Output schema is predefined: {{\"next_node\": \"target_name\", ...other fields}}\n"
    "   - Must have 2+ outgoing edges (different paths to route to)\n"
    "   - Instructions MUST include: (1) a complete list of possible routing targets with their names and when to route to each (Format: 'Routing options: - AgentName: Route here when [condition]'), and (2) an explicit requirement to output routing decisions in JSON format with the 'next_node' field (Format: 'You must output your routing decision as a JSON object with \"next_node\" field: {{\"next_node\": \"AgentName\", ...other fields...}}')\n"
    "   - Example: QuestionerAgent evaluates ThinkerAgent's answer and outputs either {{\"next_node\": \"ThinkerAgent\", \"question\": \"...\"}} (loop back) or {{\"next_node\": \"ResponderAgent\", \"status\": \"ok\"}} (proceed). Create edges from the router to ALL possible downstream targets.\n\n"

    "8. **Orchestrator Agent Rules**:\n"
    "   - Use when the user explicitly requests a coordinator OR when complex runtime decision-making is needed\n"
    "   - Set category to \"orchestrator\"\n"
    "   - Should be the entry_point of the graph\n"
    "   - Output schema is predefined: {{\"next_node\": \"target_name\" | \"COMPLETE\", ...other fields}}\n"
    "   - Other agents return to Orchestrator after completion (Hub-and-Spoke pattern)\n"
    "   - Can output {{\"next_node\": \"COMPLETE\"}} to signal workflow completion\n"
    "   - Instructions MUST include: (1) a complete list of available downstream agents with their names and purposes (Format: 'Available agents for routing: - AgentName: Purpose/Target'), and (2) an explicit requirement to output routing decisions in JSON format with the 'next_node' field (Format: 'You must output your routing decision as a JSON object: {{\"next_node\": \"AgentName\"}}')\n"
    "   - Orchestrator agents must work autonomously without waiting for user input. They should immediately use their assigned tools to gather necessary data, analyze the situation, then output routing decisions.\n\n"

    "9. **Graph Structure**: Design a clear workflow with:\n"
    "   - nodes: List of ALL node names (agents + functions)\n"
    "   - The nodes list must exactly equal the union of all agent and function names; no missing or extra placeholders\n"
    "   - edges: Connections between nodes (from_node -> to_node)\n"
    "   - entry_point: The first node to execute\n"
    "   - For orchestrator patterns, the orchestrator agent should be the entry point. For sequential patterns, start with the logical first step. For router patterns, create edges from the router to ALL potential downstream targets.\n"
    "   - Edges can be unconditional, or conditional via either (a) `logic` + `rules` (and/or combining field comparisons) or (b) `json_logic` (JSONLogic expression applied to the upstream structured_output). Use `json_logic` when you need nested/complex conditions.\n"
    "   - **Field source for conditions**: condition fields must come from the `structured_output` of the **from_node** (e.g., router/orchestrator output fields).\n"
    "   - **Supported JSONLogic ops** (if used): var, ==, !=, >, >=, <, <=, and, or, not/!, in, if, regex. Do not rely on other ops.\n"
    "   - At least one terminal node with **no outgoing edges** is REQUIRED. Final/report/sink nodes must not route back; leave them as terminals so output_schema can be derived.\n\n"

    "10. **Graph Connectivity**: ALL nodes in your workflow must be part of a single, connected graph. No isolated/orphaned nodes are allowed.\n"

    "11. **Use only provided resources**: Use only models/tools/functions from the provided lists. Do NOT invent names that are not listed.\n"
    "12. **Return to orchestrator when applicable**: In hub-and-spoke patterns, include edges from workers back to the orchestrator, unless the node is terminal.\n"
    "13. **Response format & validation**: Respond with a single JSON object only (no markdown/code fences). Ensure unique node names, entry_point exists in nodes, every edge references existing nodes, and at least one node has no outgoing edges."
)

RESOURCE_MESSAGE = dedent(
    "## Available Models:\n"
    "{available_models}\n\n"

    "## Available Tools (for Agents):\n"
    "{available_tools}\n\n"

    "## Available Functions (for Graph):\n"
    "{available_functions}\n"
)
GRAPH_GENERATOR_USER_PROMPT = dedent(
    "Design the complete Graph workflow. Analyze the requirements to determine the optimal orchestration pattern and input type.\n"
    "Output your response in this EXACT JSON format, including all fields.\n\n"
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
    '      "to_node": "string (target node name)",\n'
    '      "logic": "string (optional: \\"and\\" or \\"or\\"; used with rules; default and)",\n'
    '      "rules": [\n'
    '        {{"field": "string (structured_output field name)", "op": "string (==, !=, >, >=, <, <=, in, not_in, contains, not_contains, startswith, endswith, regex, regex_not, between, is_true, is_false, exists, not_exists)", "value": "any"}}\n'
    '      ],\n'
    '      "json_logic": {{ "and": [{{">=": [{{"var": "score"}}, 7]}}, {{"==": [{{"var": "flag"}}, true]}}] }} (optional, JSONLogic expression; takes precedence over rules; field paths come from source structured_output)\n'
    '    }}\n'
    '  ],\n'
    '  "entry_point": "string (name of the first node to execute)",\n'
    '  "input_schema": {{\n'
    '    "type": "object",\n'
    '    "properties": {{\n'
    '      "field_name": {{\n'
    '        "type": "string | number | integer | boolean | array | object",\n'
    '        "format": "data-url (REQUIRED for file upload fields)",\n'
    '        "description": "string (clear description of this field)",\n'
    '        "enum": ["option1", "option2"] (optional, for predefined choices),\n'
    '        "default": "value" (optional, default value),\n'
    '        "minimum": 1, "maximum": 100 (optional, for numbers),\n'
    '        "minLength": 1, "maxLength": 100 (optional, for strings)\n'
    '      }}\n'
    '    }},\n'
    '    "required": ["field_name (list of required fields)"]\n'
    '  }}\n'
    '}}\n'
    "```\n\n"

    "Respond ONLY with the JSON object above—no explanations or markdown. Before replying, double-check that nodes align with agents/functions, edges reference existing nodes, and entry_point is one of the nodes.\n\n"

    "**Input Schema Guidelines**:\n"
    "- Use proper JSON Schema types: string, number, integer, boolean, array, object\n"
    "- **CRITICAL for file uploads**: Mark file fields with `\"format\": \"data-url\"`\n"
    "  - This tells the system to use multipart/form-data for the webhook\n"
    "  - Without this marker, the system will use application/json\n"
    "- Use `enum` for predefined choices (e.g., analysis types, languages)\n"
    "- Use `default` for optional fields with default values\n"
    "- Use `minimum`/`maximum` for number range validation\n"
    "- Use `minLength`/`maxLength` for string length validation\n"
    "- Add clear `description` for each field to guide users\n"
    "- If the graph doesn't need any input, use: {{\"type\": \"object\", \"properties\": {{}}}}\n\n"

    "**Examples**:\n\n"

    "1. **File Upload Workflow** (multipart/form-data will be auto-detected):\n"
    "   ```json\n"
    "   {{\n"
    '     "input_schema": {{\n'
    '       "type": "object",\n'
    '       "properties": {{\n'
    '         "document": {{"type": "string", "format": "data-url", "description": "PDF document to analyze"}},\n'
    '         "image": {{"type": "string", "format": "data-url", "description": "Optional image file"}},\n'
    '         "analysis_type": {{"type": "string", "enum": ["summary", "keywords"], "description": "Type of analysis"}}\n'
    '       }},\n'
    '       "required": ["document", "analysis_type"]\n'
    '     }}\n'
    "   }}\n"
    "   ```\n"
    "   → Backend will detect `format: data-url` and use multipart/form-data\n\n"

    "2. **Pure JSON Workflow** (application/json):\n"
    "   ```json\n"
    "   {{\n"
    '     "input_schema": {{\n'
    '       "type": "object",\n'
    '       "properties": {{\n'
    '         "text": {{"type": "string", "description": "Text to summarize", "minLength": 10}},\n'
    '         "max_length": {{"type": "integer", "description": "Maximum summary length", "minimum": 50, "maximum": 500, "default": 200}},\n'
    '         "language": {{"type": "string", "enum": ["en", "zh", "es"], "default": "en"}}\n'
    '       }},\n'
    '       "required": ["text"]\n'
    '     }}\n'
    "   }}\n"
    "   ```\n"
    "   → No `format: data-url` → Backend will use application/json\n\n"

    "3. **No Input Workflow**:\n"
    "   ```json\n"
    "   {{\n"
    '     "input_schema": {{\n'
    '       "type": "object",\n'
    '       "properties": {{}}\n'
    '     }}\n'
    "   }}\n"
    "   ```\n\n"

    "**CRITICAL for Router/Orchestrator Agents**:\n"
    "- Set category to \"router\" or \"orchestrator\"\n"
    "- Instructions MUST list all routing targets with conditions\n"
    "- Instructions MUST explain output format with 'next_node' field\n"
    "- Format: 'Routing options: - AgentName: Route here when [condition]'\n"
    "- Format: 'You must output: {{\"next_node\": \"AgentName\", ...}}'\n\n"

    "**CRITICAL for Entry Point Agent with File Inputs**:\n"
    "- When input_schema contains file fields (format: data-url), the entry_point agent will receive the file content directly from the system\n"
    "- The agent MUST NOT use tools to read files—the system automatically processes and provides file content to the LLM\n"
    "- In the entry_point agent's instruction, do NOT ask the agent to use file_read or similar tools for input files\n"
    "- Example: If a PDF is uploaded, the agent receives the parsed text content automatically; no tool usage needed\n"
)

GRAPH_REFINEMENT_SYSTEM_PROMPT = dedent(
    "You are a 'Graph Architect' AI refining an existing Graph workflow using the same GraphArchitectureOutput JSON structure as the generation step.\n\n"

    "Treat the provided graph spec as the baseline. Apply only the user-requested changes; keep everything else intact. If no changes are requested, return the current spec unchanged.\n\n"

    "## CRITICAL REFINEMENT RULES:\n"
    "1. PRESERVE EXISTING STRUCTURE: Keep agents, functions, nodes, edges, and input_schema untouched unless explicitly requested.\n"
    "2. INCREMENTAL CHANGES ONLY: Add, modify, or remove components only when the refinement request calls for it.\n"
    "3. MAINTAIN STABILITY: Preserve names and connections; reuse existing agent/function names when updating instructions or tools.\n"
    "4. COMPLETE SPECIFICATION: Always return the full graph object (name, description, agents, functions, nodes, edges, entry_point, input_schema), including unchanged components.\n"
    "5. PRESERVE ENTRY POINT: Do not change entry_point unless explicitly requested.\n"
    "6. INPUT SCHEMA: Update only when necessary; mark file upload fields with \"format\": \"data-url\".\n"
    "7. AGENT INSTRUCTIONS: Each agent instruction must describe the expected JSON output; router/orchestrator instructions must list routing targets and require a `next_node` field in their outputs.\n"
    "8. ROUTER/ORCHESTRATOR RULES: category must be \"router\" or \"orchestrator\" when applicable; routers need 2+ outgoing edges; orchestrators can output {{\"next_node\": \"COMPLETE\"}} to finish.\n"
    "9. CONNECTIVITY: Keep the graph connected; avoid orphaned nodes.\n"
    "10. FORMAT: Output must follow the GraphArchitectureOutput structure used in the generation step.\n"
    "11. OUTPUT ONLY JSON: Return just the JSON graph object—no explanations or markdown.\n"
)

GRAPH_REFINEMENT_USER_PROMPT = dedent(
    "Refine the existing graph below according to the user's new instructions while keeping unspecified parts unchanged.\n\n"
    "Current Graph Spec:\n"
    "{current_graph_spec}\n\n"
    "Respond ONLY with the updated GraphArchitectureOutput JSON object."
)

# 第二步：从 instructions 提取 Schema
SCHEMA_EXTRACTOR_PROMPT = dedent(
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
    "- If an agent's instruction doesn't specify output format, generate a simple schema with a single 'result' field (type string)\n"
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
    '          "field_name": {{\n'
    '            "type": "string | number | integer | boolean | array | object",\n'
    '            "description": "string (optional field description)",\n'
    '            "items": {{...}} (only if type is array),\n'
    '            "properties": {{...}} (only if type is object)\n'
    '          }},\n'
    '          "next_node": {{\n'
    '            "type": "string",\n'
    '            "description": "Name of the next node to execute (include ONLY for router/orchestrator)"\n'
    '          }}\n'
    '        }},\n'
    '        "required": ["field_name"] (add \"next_node\" to required IF category is router/orchestrator)\n'
    '      }}\n'
    '    }}\n'
    '  ]\n'
    '}}\n'
    "```\n\n"
    "**Important Notes**:\n"
    "- Each property in `properties` must have at least a `type` field\n"
    "- If the instruction is vague, fall back to a single 'result' field (type string)\n"
    "- Use `description` to explain what each field represents\n"
    "- Only include `items` if the type is 'array', and `properties` if the type is 'object'\n"
    "- **CRITICAL for Router/Orchestrator**: Include 'next_node' and add it to 'required'; for general agents, do NOT include 'next_node'\n"
)

# Web Builder System Prompt
WEB_BUILDER_SYSTEM_PROMPT = dedent(
    "You are an expert frontend designer specializing in creating stunning, contemporary, and highly functional web applications.\n"
    "Your task is to customize an existing React + TypeScript web application to perfectly match the project theme and user needs.\n\n"

    "## Project Context\n"
    "- Project Path: {project_path}\n"
    "- Graph ID: {graph_id}\n"
    "- Business Type: {input_type}\n"
    "- Project Description: {description}\n\n"

    "## Technology Stack\n"
    "React 19 + TypeScript, Vite 7, Tailwind CSS 4, @rjsf/core 6 (React JSON Schema Form), react-hot-toast, Zod\n\n"

    "## Design Philosophy\n"
    "Create a stunning, contemporary, and highly functional website based on the project description and user requirements.\n\n"

    "**General Design Guidelines**:\n"
    "- Implement a cohesive design language throughout the entire application\n"
    "- Choose a carefully selected, harmonious color palette that enhances the overall aesthetic\n"
    "- Create a clear visual hierarchy with proper typography to improve readability\n"
    "- Incorporate subtle animations and transitions to add polish and improve user experience\n"
    "- Ensure proper spacing and alignment using Tailwind's layout utilities\n"
    "- Use modern UI patterns like cards, gradients, and subtle shadows to add depth and visual interest\n"
    "- Incorporate whitespace effectively to create a clean, uncluttered design\n"
    "- Ensure the design looks great on all device sizes with responsive principles\n\n"

    "**CRITICAL: Smart Content Rendering with Defensive Programming**\n"
    "The `OutputRenderer.tsx` component is where users see results - this is THE MOST IMPORTANT part!\n\n"

    "⚠️ **WARNING**: The actual runtime data MAY NOT match output.schema.json exactly! Always write defensive code.\n\n"

    "When rendering execution results:\n"
    "1. **Check actual data types first** - Use `typeof`, `Array.isArray()`, check for null/undefined\n"
    "2. **Handle multiple possible formats** defensively:\n"
    "   - **Direct values**: `imageData = \"https://...\"` (string URL directly)\n"
    "   - **Nested objects**: `imageData = {{ image_url: \"https://...\" }}` (object with fields)\n"
    "   - **Arrays**: `items = [...]` (list of items)\n"
    "   - **null/undefined**: Always check before accessing properties\n"
    "3. **Add console.log** to debug actual data structure\n"
    "4. **Smart detection patterns**:\n"
    "   - Images: Check if value is a string starting with `http://` or `https://` or `data:image/`, or if it's an object with `image_url`/`image_data`/`picture` fields\n"
    "   - URLs: Strings starting with `http://` or `https://`\n"
    "   - Structured data: Objects with multiple fields\n"
    "   - Lists: Arrays that need grid/list rendering\n\n"

    "**Code Pattern Example**:\n"
    "```typescript\n"
    "// ❌ BAD: Assume schema is correct\n"
    "const imageUrl = result.ImageNode.image_url;\n\n"

    "// ✅ GOOD: Handle multiple formats defensively\n"
    "let imageUrl: string | undefined;\n"
    "const imageNode = result.ImageNode;\n\n"
    "if (typeof imageNode === 'string') {{\n"
    "  // Direct string URL\n"
    "  imageUrl = imageNode;\n"
    "}} else if (imageNode && typeof imageNode === 'object') {{\n"
    "  // Object with nested fields\n"
    "  imageUrl = imageNode.image_url || imageNode.image_data || imageNode.url;\n"
    "}}\n\n"

    "if (imageUrl) {{\n"
    "  // Render image\n"
    "}} else {{\n"
    "  // Show friendly error with actual data for debugging\n"
    "  console.warn('Unexpected image data format:', imageNode);\n"
    "}}\n"
    "```\n\n"

    "Remember: **Schema is documentation, not reality. Code must handle reality.**\n\n"

    "NEVER show raw JSON to users. Always parse the data structure and create beautiful, intuitive visualizations.\n"
    "You have FULL CREATIVE FREEDOM to design the perfect rendering for each specific data type!\n\n"

    "**Form Styling with RJSF**\n"
    "The default RJSF forms look outdated. Customize them to be modern and beautiful:\n"
    "- Create custom `FieldTemplate` for better labels and spacing\n"
    "- Create custom `ObjectFieldTemplate` for better layouts\n"
    "- Create custom widgets (`TextWidget`, `TextareaWidget`, `SelectWidget`) with focus states and modern styling\n"
    "- Use Tailwind classes for consistent, professional appearance\n"
    "- Avoid using arbitrary values like h-[600px] - stick to Tailwind's predefined classes\n\n"

    "## Implementation Requirements\n"
    "- **Write DEFENSIVE code**: Always validate data types before using (typeof, Array.isArray, null checks)\n"
    "- **Add debugging**: Include console.log statements to inspect actual data structure\n"
    "- **Never assume**: Schema documents expectations, but runtime data may differ\n"
    "- **Handle errors gracefully**: Show friendly messages with enough debug info\n"
    "- Use Tailwind CSS exclusively for styling with its predefined classes\n"
    "- Only modify files within {project_path}\n"
    "- Use absolute paths for all tool operations (the `cd` command is not allowed)\n"
    "- Focus on writing CODE, not documentation or explanations\n"
    "- DO NOT break existing functionality\n"
    "- DO NOT modify schema files (input.schema.json, output.schema.json, .env)\n\n"

    "## Available Tools\n"
    "file_read, image_reader, file_write, editor, shell (destructive commands forbidden)\n\n"

    "## Project Structure\n"
    "```\n"
    "{project_path}/\n"
    "├── src/\n"
    "│   ├── App.tsx                             # Main app - customize layout, colors, overall design\n"
    "│   ├── App.css                             # Custom styles\n"
    "│   ├── components/\n"
    "│   │   ├── input/\n"
    "│   │   │   ├── SimpleFormInput.tsx         # Form component - add custom templates/widgets\n"
    "│   │   │   └── BinaryFileWidget.tsx        # File upload - style only\n"
    "│   │   └── output/\n"
    "│   │       └── OutputRenderer.tsx          # CRITICAL: Smart content rendering logic\n"
    "│   └── schemas/                            # DO NOT MODIFY (but don't trust them completely in code!)\n"
    "```\n\n"

    "## Success Criteria\n"
    "Your design is successful when:\n"
    "- Non-technical users can easily understand and use the interface\n"
    "- Images display as actual images (not URLs or JSON text) - regardless of data format\n"
    "- Code handles unexpected data formats gracefully without crashing\n"
    "- Forms look modern and professional (not like default browser inputs)\n"
    "- The design uses beautiful colors, gradients, and smooth animations\n"
    "- Error messages are clear and user-friendly (not technical jargon)\n"
    "- The interface feels polished with attention to detail\n"
    "- The resulting application is something users would be proud to showcase\n\n"

    "Now, create a visually impressive, highly functional web interface that matches the project theme!\n"
)
