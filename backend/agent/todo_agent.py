"""Groq-based Todo Agent with manual function calling."""
import json
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from groq import Groq
from sqlmodel import Session
from dotenv import load_dotenv

from agent.mcp_tools import call_mcp_tool

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


SYSTEM_PROMPT = """You are a todo list assistant. You help users manage tasks by calling functions.

When user wants to manage tasks, respond with a function call in this JSON format:
{"function": "function_name", "arguments": {"arg": "value"}}

Available functions:
- add_task: Create task. Args: title (string, required)
- list_tasks: Show all tasks. Args: none
- complete_task: Mark done. Args: task_id (number)
- delete_task: Remove task. Args: task_id (number)
- update_task: Edit task. Args: task_id (number), title (string)

Examples:
User: add task buy milk
Response: {"function": "add_task", "arguments": {"title": "buy milk"}}

User: show tasks
Response: {"function": "list_tasks", "arguments": {}}

User: complete task 1
Response: {"function": "complete_task", "arguments": {"task_id": 1}}

User: delete task 2
Response: {"function": "delete_task", "arguments": {"task_id": 2}}

Always respond with JSON for task operations. No other text."""


class TodoAgent:
    """Groq-based agent for todo management."""

    def __init__(self):
        self.model = "llama-3.1-8b-instant"

    def _parse_function_call(self, text: str) -> Optional[Dict]:
        """Extract function call JSON from text."""
        print(f"[PARSE] Input text: {text}")

        # Try to find any JSON object in the text
        try:
            # Method 1: Direct JSON parse if whole response is JSON
            stripped = text.strip()
            if stripped.startswith('{') and stripped.endswith('}'):
                data = json.loads(stripped)
                if "function" in data:
                    print(f"[PARSE] Found direct JSON: {data}")
                    return data
        except:
            pass

        # Method 2: Find JSON in code blocks
        code_block = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text)
        if code_block:
            try:
                data = json.loads(code_block.group(1))
                if "function" in data:
                    print(f"[PARSE] Found in code block: {data}")
                    return data
            except:
                pass

        # Method 3: Find JSON anywhere in text
        json_match = re.search(r'\{[^{}]*"function"[^{}]*\}', text)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                print(f"[PARSE] Found inline JSON: {data}")
                return data
            except:
                pass

        # Method 4: More aggressive search
        json_match = re.search(r'\{.*?"function"\s*:\s*"(\w+)".*?"arguments"\s*:\s*(\{[^}]*\}).*?\}', text, re.DOTALL)
        if json_match:
            try:
                func_name = json_match.group(1)
                args_str = json_match.group(2)
                args = json.loads(args_str)
                result = {"function": func_name, "arguments": args}
                print(f"[PARSE] Reconstructed JSON: {result}")
                return result
            except:
                pass

        print("[PARSE] No function call found")
        return None

    def process_message(
        self,
        session: Session,
        user_id: str,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Process a user message."""
        tool_calls_made = []

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if chat_history:
            for msg in chat_history:
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": message})

        print(f"\n{'='*50}")
        print(f"[AGENT] User: {message}")

        # Get LLM response
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=512,
            temperature=0.1
        )

        llm_response = response.choices[0].message.content or ""
        print(f"[AGENT] LLM Response: {llm_response}")

        # Try to parse function call
        func_call = self._parse_function_call(llm_response)

        if func_call:
            func_name = func_call.get("function")
            func_args = func_call.get("arguments", {})

            if func_name:
                # Add user_id
                func_args["user_id"] = user_id

                print(f"[AGENT] Executing: {func_name}({func_args})")

                # Execute function
                result = call_mcp_tool(session, func_name, func_args)
                print(f"[AGENT] Result: {result}")

                # Record tool call
                tool_calls_made.append({
                    "name": func_name,
                    "arguments": {k: v for k, v in func_args.items() if k != "user_id"},
                    "result": result
                })

                # Generate human response based on result
                if func_name == "add_task":
                    response_text = f"Added task: '{result.get('title')}' (ID: {result.get('task_id')})"
                elif func_name == "list_tasks":
                    tasks = result.get("tasks", [])
                    if tasks:
                        lines = []
                        for t in tasks:
                            status = "done" if t["completed"] else "pending"
                            lines.append(f"  {t['id']}. {t['title']} [{status}]")
                        response_text = "Your tasks:\n" + "\n".join(lines)
                    else:
                        response_text = "You have no tasks yet. Try adding one!"
                elif func_name == "complete_task":
                    if result.get("status") in ["completed", "uncompleted"]:
                        status_word = "complete" if result.get("status") == "completed" else "incomplete"
                        response_text = f"Marked '{result.get('title')}' as {status_word}!"
                    else:
                        response_text = f"Task not found."
                elif func_name == "delete_task":
                    if result.get("status") == "deleted":
                        response_text = f"Deleted '{result.get('title')}'"
                    else:
                        response_text = f"Task not found."
                elif func_name == "update_task":
                    if result.get("status") == "updated":
                        response_text = f"Updated task to '{result.get('title')}'"
                    else:
                        response_text = f"Task not found."
                else:
                    response_text = "Done!"
        else:
            # No function call - just return LLM response or help message
            response_text = llm_response if llm_response else "I can help you manage tasks. Try: 'add task buy groceries' or 'show tasks'"

        print(f"[AGENT] Final response: {response_text}")
        print(f"{'='*50}\n")

        return response_text, tool_calls_made


todo_agent = TodoAgent()
