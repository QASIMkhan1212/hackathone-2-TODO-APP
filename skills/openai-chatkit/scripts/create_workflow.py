#!/usr/bin/env python3
"""
Helper script to create ChatKit workflows via OpenAI API.
"""

import os
import sys
import json
import argparse
from openai import OpenAI

def create_workflow(
    name,
    instructions,
    model="gpt-4o",
    tools=None,
    temperature=0.7,
    api_key=None
):
    """Create a new ChatKit workflow."""
    client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))

    workflow_config = {
        "name": name,
        "model": model,
        "instructions": instructions,
        "temperature": temperature
    }

    if tools:
        workflow_config["tools"] = tools

    try:
        # Note: This uses hypothetical API structure
        # Actual implementation may differ - check OpenAI docs
        response = client.agent_builder.workflows.create(**workflow_config)

        print(f"✅ Workflow created successfully!")
        print(f"Workflow ID: {response.id}")
        print(f"Name: {response.name}")
        print(f"Model: {response.model}")

        return response

    except Exception as e:
        print(f"❌ Error creating workflow: {str(e)}")
        sys.exit(1)

def list_workflows(api_key=None):
    """List all existing workflows."""
    client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))

    try:
        workflows = client.agent_builder.workflows.list()

        print("\nExisting Workflows:")
        print("-" * 60)

        for workflow in workflows.data:
            print(f"ID: {workflow.id}")
            print(f"Name: {workflow.name}")
            print(f"Model: {workflow.model}")
            print("-" * 60)

    except Exception as e:
        print(f"❌ Error listing workflows: {str(e)}")

def get_workflow_templates():
    """Return pre-built workflow templates."""
    return {
        "customer_support": {
            "name": "Customer Support Agent",
            "instructions": """You are a helpful customer support agent.
Your goal is to assist customers with their inquiries about products,
orders, returns, and general questions. Be friendly, professional,
and solution-oriented. If you cannot help with something, escalate
to a human agent.""",
            "tools": [
                {"type": "web_search"},
                {"type": "code_interpreter"}
            ]
        },
        "sales_assistant": {
            "name": "Sales Assistant",
            "instructions": """You are a knowledgeable sales assistant.
Help customers discover products, answer questions about features
and pricing, and guide them through the purchase process.
Be consultative and focus on understanding customer needs.""",
            "tools": [{"type": "web_search"}]
        },
        "technical_support": {
            "name": "Technical Support Agent",
            "instructions": """You are a technical support specialist.
Help users troubleshoot technical issues, provide step-by-step
solutions, and explain technical concepts clearly. When appropriate,
provide code examples or configuration details.""",
            "tools": [
                {"type": "web_search"},
                {"type": "code_interpreter"}
            ]
        },
        "general_assistant": {
            "name": "General AI Assistant",
            "instructions": """You are a helpful AI assistant.
Answer questions, provide information, help with tasks,
and engage in meaningful conversations. Be helpful,
accurate, and friendly.""",
            "tools": [
                {"type": "web_search"},
                {"type": "code_interpreter"}
            ]
        }
    }

def main():
    parser = argparse.ArgumentParser(
        description="Create and manage ChatKit workflows"
    )
    parser.add_argument(
        "action",
        choices=["create", "list", "template"],
        help="Action to perform"
    )
    parser.add_argument(
        "--name",
        help="Workflow name"
    )
    parser.add_argument(
        "--instructions",
        help="System instructions for the workflow"
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="Model to use (default: gpt-4o)"
    )
    parser.add_argument(
        "--tools",
        nargs="+",
        help="Tools to enable (web_search, code_interpreter)"
    )
    parser.add_argument(
        "--template",
        choices=["customer_support", "sales_assistant", "technical_support", "general_assistant"],
        help="Use a pre-built template"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )

    args = parser.parse_args()

    if args.action == "list":
        list_workflows(api_key=args.api_key)

    elif args.action == "template":
        templates = get_workflow_templates()
        print("\nAvailable Templates:")
        print("=" * 60)
        for key, template in templates.items():
            print(f"\nTemplate: {key}")
            print(f"Name: {template['name']}")
            print(f"Instructions: {template['instructions'][:100]}...")
            print(f"Tools: {[t['type'] for t in template.get('tools', [])]}")

    elif args.action == "create":
        if args.template:
            # Use template
            templates = get_workflow_templates()
            template = templates[args.template]

            create_workflow(
                name=template["name"],
                instructions=template["instructions"],
                model=args.model,
                tools=template.get("tools"),
                api_key=args.api_key
            )

        elif args.name and args.instructions:
            # Create custom workflow
            tools = None
            if args.tools:
                tools = [{"type": tool} for tool in args.tools]

            create_workflow(
                name=args.name,
                instructions=args.instructions,
                model=args.model,
                tools=tools,
                api_key=args.api_key
            )

        else:
            print("Error: Either --template or both --name and --instructions required")
            sys.exit(1)

if __name__ == "__main__":
    main()
