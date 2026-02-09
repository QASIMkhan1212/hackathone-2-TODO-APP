#!/usr/bin/env python3
"""
Initialize ChatKit in a new or existing project.
Creates necessary files, installs dependencies, and sets up configuration.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return None

def detect_framework(project_path):
    """Detect the framework used in the project."""
    package_json = project_path / "package.json"

    if not package_json.exists():
        return None

    with open(package_json) as f:
        data = json.load(f)
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

        if "next" in deps:
            return "nextjs"
        elif "react" in deps and "react-dom" in deps:
            return "react"
        elif "vue" in deps:
            return "vue"
        elif "angular" in deps or "@angular/core" in deps:
            return "angular"

    return "vanilla"

def install_dependencies(project_path, framework):
    """Install ChatKit dependencies."""
    print("Installing ChatKit dependencies...")

    if framework in ["react", "nextjs"]:
        cmd = "npm install @openai/chatkit-react openai"
    elif framework == "vue":
        cmd = "npm install @openai/chatkit-react openai"
    else:
        cmd = "npm install @openai/chatkit-web openai"

    result = run_command(cmd, cwd=project_path)
    if result is not None:
        print("Dependencies installed successfully!")
        return True
    return False

def create_env_file(project_path):
    """Create or update .env file with ChatKit configuration."""
    env_file = project_path / ".env.local"
    env_example = project_path / ".env.example"

    env_content = """# OpenAI ChatKit Configuration
OPENAI_API_KEY=your_openai_api_key_here
CHATKIT_WORKFLOW_ID=your_workflow_id_here

# For Next.js (exposed to browser)
NEXT_PUBLIC_WORKFLOW_ID=your_workflow_id_here
"""

    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print(f"Created {env_file}")

    if not env_example.exists():
        with open(env_example, "w") as f:
            f.write(env_content)
        print(f"Created {env_example}")

def create_nextjs_api_route(project_path, app_router=True):
    """Create ChatKit session API route for Next.js."""
    if app_router:
        api_dir = project_path / "app" / "api" / "chatkit-session"
        api_dir.mkdir(parents=True, exist_ok=True)
        api_file = api_dir / "route.ts"

        content = """import { NextResponse } from 'next/server';
import OpenAI from 'openai';

export async function POST() {
  try {
    const client = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });

    const session = await client.chatkit.sessions.create({
      workflow_id: process.env.CHATKIT_WORKFLOW_ID!
    });

    return NextResponse.json({
      clientSecret: session.client_secret
    });
  } catch (error) {
    console.error('ChatKit session creation error:', error);
    return NextResponse.json(
      { error: 'Failed to create session' },
      { status: 500 }
    );
  }
}
"""
    else:
        api_dir = project_path / "pages" / "api"
        api_dir.mkdir(parents=True, exist_ok=True)
        api_file = api_dir / "chatkit-session.ts"

        content = """import type { NextApiRequest, NextApiResponse } from 'next';
import OpenAI from 'openai';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const client = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });

    const session = await client.chatkit.sessions.create({
      workflow_id: process.env.CHATKIT_WORKFLOW_ID!
    });

    res.json({ clientSecret: session.client_secret });
  } catch (error) {
    console.error('ChatKit session creation error:', error);
    res.status(500).json({ error: 'Failed to create session' });
  }
}
"""

    with open(api_file, "w") as f:
        f.write(content)
    print(f"Created API route: {api_file}")

def create_react_component(project_path):
    """Create example ChatKit React component."""
    components_dir = project_path / "src" / "components"
    components_dir.mkdir(parents=True, exist_ok=True)
    component_file = components_dir / "ChatKitComponent.tsx"

    content = """'use client'; // Remove this line if not using Next.js App Router

import { useChatKit, ChatKit } from '@openai/chatkit-react';

export default function ChatKitComponent() {
  const { session, error, isLoading } = useChatKit({
    workflowId: process.env.NEXT_PUBLIC_WORKFLOW_ID!,
    getClientSecret: async () => {
      const res = await fetch('/api/chatkit-session', {
        method: 'POST'
      });

      if (!res.ok) {
        throw new Error('Failed to create session');
      }

      const data = await res.json();
      return data.clientSecret;
    }
  });

  if (isLoading) {
    return <div className="chatkit-loading">Loading chat...</div>;
  }

  if (error) {
    return (
      <div className="chatkit-error">
        Error loading chat: {error.message}
      </div>
    );
  }

  return (
    <div className="chatkit-container">
      <ChatKit
        session={session}
        theme={{
          primaryColor: '#0066cc',
          fontFamily: 'system-ui, sans-serif'
        }}
      />
    </div>
  );
}
"""

    with open(component_file, "w") as f:
        f.write(content)
    print(f"Created component: {component_file}")

def create_readme(project_path):
    """Create ChatKit setup README."""
    readme = project_path / "CHATKIT_SETUP.md"

    content = """# ChatKit Setup Guide

## Configuration

1. Update your `.env.local` file with your OpenAI credentials:
   ```
   OPENAI_API_KEY=your_actual_api_key
   CHATKIT_WORKFLOW_ID=your_actual_workflow_id
   NEXT_PUBLIC_WORKFLOW_ID=your_actual_workflow_id
   ```

2. Get your API key from: https://platform.openai.com/api-keys

3. Create a workflow:
   - Visit https://platform.openai.com/agent-builder
   - Create a new workflow or use existing one
   - Copy the workflow ID

## Usage

Import and use the ChatKit component:

```tsx
import ChatKitComponent from '@/components/ChatKitComponent';

function Page() {
  return (
    <div>
      <h1>My App</h1>
      <ChatKitComponent />
    </div>
  );
}
```

## Customization

Modify the theme in `ChatKitComponent.tsx`:

```tsx
<ChatKit
  session={session}
  theme={{
    primaryColor: '#your-brand-color',
    fontFamily: 'your-font',
    borderRadius: '0.5rem'
  }}
/>
```

## Resources

- ChatKit Docs: https://platform.openai.com/docs/guides/chatkit
- Agent Builder: https://platform.openai.com/agent-builder
- Examples: https://github.com/openai/chatkit-js
"""

    with open(readme, "w") as f:
        f.write(content)
    print(f"Created setup guide: {readme}")

def main():
    parser = argparse.ArgumentParser(
        description="Initialize ChatKit in your project"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Project directory (default: current directory)"
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip installing npm dependencies"
    )
    parser.add_argument(
        "--pages-router",
        action="store_true",
        help="Use Next.js Pages Router instead of App Router"
    )

    args = parser.parse_args()
    project_path = Path(args.path).resolve()

    if not project_path.exists():
        print(f"Error: Directory {project_path} does not exist")
        sys.exit(1)

    print(f"Initializing ChatKit in: {project_path}")

    # Detect framework
    framework = detect_framework(project_path)
    print(f"Detected framework: {framework or 'unknown'}")

    # Install dependencies
    if not args.skip_install and framework:
        if not install_dependencies(project_path, framework):
            print("Warning: Failed to install dependencies")

    # Create environment file
    create_env_file(project_path)

    # Create framework-specific files
    if framework == "nextjs":
        create_nextjs_api_route(
            project_path,
            app_router=not args.pages_router
        )
        create_react_component(project_path)
    elif framework == "react":
        create_react_component(project_path)
        print("Note: You'll need to create your own backend endpoint for session creation")

    # Create setup guide
    create_readme(project_path)

    print("\nChatKit initialization complete!")
    print("\nNext steps:")
    print("1. Update .env.local with your OpenAI API key and workflow ID")
    print("2. Review CHATKIT_SETUP.md for usage instructions")
    print("3. Import and use ChatKitComponent in your app")

if __name__ == "__main__":
    main()
