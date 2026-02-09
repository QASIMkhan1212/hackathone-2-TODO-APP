"""Multi-agent system template for OpenAI Agents SDK.

This template demonstrates a router-based multi-agent architecture
with specialized agents, handoffs, and shared sessions.
"""

import os
from typing import Optional

from agents import (
    Agent,
    Runner,
    function_tool,
    SQLiteSession,
    ModelSettings,
)


# =============================================================================
# Configuration
# =============================================================================

assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY environment variable required"


# =============================================================================
# Shared Tools (available to multiple agents)
# =============================================================================


@function_tool
def log_interaction(agent_name: str, action: str, details: str) -> bool:
    """Log an agent interaction for auditing.

    Args:
        agent_name: Name of the agent logging
        action: Action being performed
        details: Additional details

    Returns:
        True if logged successfully
    """
    from datetime import datetime
    print(f"[{datetime.now().isoformat()}] {agent_name}: {action} - {details}")
    return True


# =============================================================================
# Sales Agent
# =============================================================================


@function_tool
def get_product_catalog(category: Optional[str] = None) -> list[dict]:
    """Get available products from the catalog.

    Args:
        category: Optional category filter

    Returns:
        List of products
    """
    # Placeholder implementation
    products = [
        {"id": "P1", "name": "Basic Plan", "price": 9.99, "category": "subscription"},
        {"id": "P2", "name": "Pro Plan", "price": 29.99, "category": "subscription"},
        {"id": "P3", "name": "Enterprise", "price": 99.99, "category": "subscription"},
    ]
    if category:
        products = [p for p in products if p["category"] == category]
    return products


@function_tool
def create_quote(product_id: str, quantity: int, customer_name: str) -> dict:
    """Create a price quote for a customer.

    Args:
        product_id: Product ID
        quantity: Number of units
        customer_name: Customer's name

    Returns:
        Quote details
    """
    return {
        "quote_id": "Q-12345",
        "product_id": product_id,
        "quantity": quantity,
        "customer": customer_name,
        "status": "pending",
    }


sales_agent = Agent(
    name="SalesAgent",
    instructions="""You are a sales specialist.

Your responsibilities:
- Answer questions about products and pricing
- Help customers choose the right plan
- Create quotes for interested customers

Guidelines:
1. Be helpful but not pushy
2. Understand customer needs before recommending
3. Always provide accurate pricing information
4. Log important interactions
""",
    tools=[get_product_catalog, create_quote, log_interaction],
    model_settings=ModelSettings(temperature=0.7),
)


# =============================================================================
# Support Agent
# =============================================================================


@function_tool
def search_documentation(query: str) -> list[dict]:
    """Search support documentation.

    Args:
        query: Search query

    Returns:
        Matching documentation articles
    """
    # Placeholder implementation
    return [
        {"title": "Getting Started Guide", "url": "/docs/getting-started"},
        {"title": "FAQ", "url": "/docs/faq"},
    ]


@function_tool
def create_support_ticket(
    subject: str,
    description: str,
    priority: str = "medium"
) -> dict:
    """Create a support ticket.

    Args:
        subject: Ticket subject
        description: Issue description
        priority: Priority level (low, medium, high)

    Returns:
        Created ticket details
    """
    return {
        "ticket_id": "T-67890",
        "subject": subject,
        "priority": priority,
        "status": "open",
    }


@function_tool
def check_service_status() -> dict:
    """Check current service status.

    Returns:
        Service health status
    """
    return {
        "status": "operational",
        "api": "operational",
        "dashboard": "operational",
        "last_incident": None,
    }


support_agent = Agent(
    name="SupportAgent",
    instructions="""You are a technical support specialist.

Your responsibilities:
- Help troubleshoot technical issues
- Search documentation for answers
- Create support tickets for complex issues
- Check service status

Guidelines:
1. First search documentation for solutions
2. Ask clarifying questions when needed
3. Create tickets for issues you can't resolve
4. Always be patient and understanding
""",
    tools=[search_documentation, create_support_ticket, check_service_status, log_interaction],
    model_settings=ModelSettings(temperature=0.3),
)


# =============================================================================
# Billing Agent
# =============================================================================


@function_tool
def get_account_balance(account_id: str) -> dict:
    """Get account balance and billing info.

    Args:
        account_id: Customer account ID

    Returns:
        Account balance details
    """
    return {
        "account_id": account_id,
        "balance": 150.00,
        "currency": "USD",
        "next_billing_date": "2025-02-01",
    }


@function_tool
def get_invoices(account_id: str, limit: int = 5) -> list[dict]:
    """Get recent invoices for an account.

    Args:
        account_id: Customer account ID
        limit: Maximum invoices to return

    Returns:
        List of invoices
    """
    return [
        {"invoice_id": "INV-001", "amount": 29.99, "status": "paid", "date": "2025-01-01"},
        {"invoice_id": "INV-002", "amount": 29.99, "status": "pending", "date": "2025-02-01"},
    ]


@function_tool
def process_refund(invoice_id: str, reason: str) -> dict:
    """Process a refund request.

    Args:
        invoice_id: Invoice to refund
        reason: Refund reason

    Returns:
        Refund status
    """
    return {
        "refund_id": "R-11111",
        "invoice_id": invoice_id,
        "status": "processing",
        "estimated_days": 5,
    }


billing_agent = Agent(
    name="BillingAgent",
    instructions="""You are a billing specialist.

Your responsibilities:
- Answer billing and payment questions
- Look up account balances and invoices
- Process refund requests

Guidelines:
1. Verify account information before sharing details
2. Be clear about billing dates and amounts
3. Follow refund policies
4. Escalate disputes to support ticket
""",
    tools=[get_account_balance, get_invoices, process_refund, log_interaction],
    model_settings=ModelSettings(temperature=0.2),
)


# =============================================================================
# Router Agent
# =============================================================================


router_agent = Agent(
    name="CustomerServiceRouter",
    instructions="""You are a customer service router.

Your job is to understand customer requests and route them to the right specialist:

1. **SalesAgent** - For:
   - Product questions
   - Pricing inquiries
   - Buying/upgrading plans
   - Quotes and proposals

2. **SupportAgent** - For:
   - Technical issues
   - How-to questions
   - Bug reports
   - Service status questions

3. **BillingAgent** - For:
   - Invoice questions
   - Payment issues
   - Refund requests
   - Account balance inquiries

Guidelines:
- Greet customers warmly
- Quickly identify their need
- Route to the appropriate specialist
- If unclear, ask one clarifying question
- For general questions, answer directly
""",
    handoffs=[sales_agent, support_agent, billing_agent],
    model_settings=ModelSettings(temperature=0.5),
)


# =============================================================================
# Session Management
# =============================================================================


def get_session(session_id: str) -> SQLiteSession:
    """Get or create a session for conversation memory.

    Args:
        session_id: Unique session identifier

    Returns:
        SQLiteSession instance
    """
    return SQLiteSession(session_id)


# =============================================================================
# Runner Functions
# =============================================================================


async def handle_customer_request(
    message: str,
    session_id: Optional[str] = None,
    max_turns: int = 20,
) -> str:
    """Handle a customer request through the multi-agent system.

    Args:
        message: Customer's message
        session_id: Optional session ID for conversation memory
        max_turns: Maximum agent turns

    Returns:
        Final response to customer
    """
    session = get_session(session_id) if session_id else None

    result = await Runner.run(
        router_agent,
        message,
        session=session,
        max_turns=max_turns,
    )

    return result.final_output


async def run_conversation(session_id: str):
    """Run an interactive conversation.

    Args:
        session_id: Session ID for this conversation
    """
    print("Customer Service System")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == 'quit':
            print("Goodbye!")
            break

        if not user_input:
            continue

        response = await handle_customer_request(user_input, session_id)
        print(f"Agent: {response}\n")


# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":
    import asyncio
    import uuid

    async def main():
        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Demo mode - run sample requests
        demo_requests = [
            "Hi, I'm interested in your Pro Plan",
            "Actually, I have a technical issue - my dashboard won't load",
            "Can you also check my account balance?",
        ]

        print("=== Multi-Agent Demo ===\n")

        for request in demo_requests:
            print(f"Customer: {request}")
            response = await handle_customer_request(request, session_id)
            print(f"Agent: {response}\n")
            print("-" * 50 + "\n")

    asyncio.run(main())
