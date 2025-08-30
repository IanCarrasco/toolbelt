from pydoc import cli
from lib.prompts.prompt_util import load_system_prompt
from openai import OpenAI
import json
import concurrent.futures
import os

import re

def extract_tool_specs(content):
    """
    Extract tool specifications from content between <tool_spec> tags.
    
    Args:
        content: The content string to extract tool specs from
        
    Returns:
        list: List of extracted tool specifications as dictionaries
    """
    tool_specs = []
    
    # Find all content between <tool_spec> and </tool_spec> tags
    pattern = r'<tool_spec>\s*(.*?)\s*</tool_spec>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        try:
            # Parse the JSON content
            tool_spec = json.loads(match.strip())
            tool_specs.append(tool_spec)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse tool_spec JSON: {e}")
            print(f"Content: {match}")
            continue
    
    return tool_specs

# Runs the full toolbelt flow for a given user request
class ToolbeltSession():
    def __init__(self, client: OpenAI, tool_dir=os.getcwd()):
        self.creation_thread = []
        self.response_thread = []
        self.client = client
        self.tool_dir = tool_dir
        self.tools_to_create = []
        self.tool_fns = {}

    # Takes in a json-schema tool spec and writes a python function that satisfies it.
    def generate_and_write_tool(self, tool):
        fn_response = self.client.responses.create(
            model="gpt-5-nano",
            input=json.dumps(tool),
            instructions=load_system_prompt("write_tool_source")
        )
        output_text = fn_response.output_text
        tool_path = os.path.join(self.tool_dir, f"lib/tools/{tool['name']}.py")
        os.makedirs(os.path.dirname(tool_path), exist_ok=True)
        with open(tool_path, 'w') as f:
            f.write(output_text)
        return output_text

    # Runs the full tool creation and tool use flow for a given user request.
    async def run(self, user_request: str):
        self.creation_thread.append({"role": "user", "content": user_request})
        
        yield "Determining necessary tool definitions..."
        tool_creation_response = self.client.responses.create(
            model="gpt-5-mini",
            input=self.creation_thread,
            instructions=load_system_prompt("tool_creation")
        )
        # Creates all necessary tool specs to satisfy the user request
        yield f"Debug: Tool creation response received with {len(tool_creation_response.output)} items"
        self.creation_thread.append(tool_creation_response.output)

        # Gather all create tool call results (json-schemas)
        self.tools_to_create.extend(extract_tool_specs(tool_creation_response.output_text))
    

        # Write the source code for each tool based on the tool definitions
        yield "Great! I need to write the source for the following tools:"
        for t in self.tools_to_create:
            yield f'{t["name"]}: {t["description"]}'

        # Write each tool's source code in parallel and store them
        yield 'Writing tool source code....'
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(executor.map(lambda t: {'name': t['name'], 'tool_fn': self.generate_and_write_tool(t)}, self.tools_to_create))
                for result in results:
                    self.tool_fns[result['name']] = result['tool_fn']
            yield f'Finished writing code for {len(results)} tools'
        except Exception as e:
            yield f'Error writing tool source code: {str(e)}'

        self.creation_thread.append({
            "role":"user",
            "content": f"I have went ahead and successfully created {len(self.tools_to_create)} tools: {','.join([t['name'] for t in self.tools_to_create])}"
        })
        
        
        # Initialize a new thread for using the newly created tools
        # Create a new tools list just containing the tools required to solve the task
        yield "Now I'll use these tools to answer your question..."
        self.response_thread.append({"role": "user", "content": user_request})
        yield "Analyzing your request and determining which tools to use..."
        
        # Ensure we have tools to work with
        if not self.tools_to_create:
            yield "No tools were created, cannot proceed with execution."
            
        use_tool_response = self.client.responses.create(
            model="gpt-5-nano",
            tools=self.tools_to_create,
            input=self.response_thread,
            instructions=load_system_prompt('use_tool'),
            tool_choice={'type':'allowed_tools', 'mode':'auto', 'tools': [{'type':'function', 'name': t['name']} for t in self.tools_to_create]},
        )

        yield f"Debug: Received use_tool_response with {len(use_tool_response.output)} items"
        
        # Extract only the serializable parts from the response
        response_items = []
        for item in use_tool_response.output:
            if item.type == "function_call":
                response_items.append({
                    "type": "function_call",
                    "name": item.name,
                    "arguments": item.arguments,
                    "call_id": item.call_id
                })
        
        self.response_thread += use_tool_response.output

        # Store the function calls we are trying to invoke to call later
        new_fn_invocations = []
        for item in response_items:
            if item["type"] == "function_call":
                function_call_arguments = json.loads(item["arguments"])
                new_fn_invocations.append((item, function_call_arguments))
        
        yield f"Debug: Processed {len(new_fn_invocations)} function invocations"
        
        if new_fn_invocations:
            yield f"I need to execute {len(new_fn_invocations)} tool(s) to answer your question..."
        else:
            yield "No tools need to be executed for this request."
        
        # Imports the newly created tool functions
        for fn, _ in new_fn_invocations:
            yield f"Importing tool: {fn['name']}..."
            try:
                exec(f"from lib.tools.{fn['name']} import {fn['name']}")
                yield f"Successfully imported tool: {fn['name']}"
            except Exception as e:
                yield f"Error importing tool {fn['name']}: {str(e)}"
                continue

        # Executes the tools
        response_tool_call_results = []
        for i, invocation in enumerate(new_fn_invocations):
            yield f"Executing tool {i+1}/{len(new_fn_invocations)}: {invocation[0]['name']}..."
            try:
                result = eval(f"{invocation[0]['name']}(**invocation[1])")
                response_tool_call_results.append({"type": "function_call_output", "call_id": invocation[0]['call_id'], "output": json.dumps(result)})
                yield f"Tool {invocation[0]['name']} completed successfully"
            except Exception as e:
                error_msg = f"Error executing tool {invocation[0]['name']}: {str(e)}"
                yield error_msg
                response_tool_call_results.append({"type": "function_call_output", "call_id": invocation[0]['call_id'], "output": json.dumps({"error": str(e)})})

        self.response_thread.extend(response_tool_call_results)

        yield "Processing the results and generating final response..."
        
        final_response = self.client.responses.create(
            model="gpt-5-mini",
            input=self.response_thread,
            instructions=load_system_prompt('tool_summary')
        )
        
        yield f'Final response: {final_response.output_text}'

if __name__ == '__main__':
    import asyncio
    client = OpenAI(api_key=os.environ['OPENAI_TOOLBELT_KEY'])
    session = ToolbeltSession(client=client)
    asyncio.run(session.run('How long would it take in seconds to walk from new york to LA'))