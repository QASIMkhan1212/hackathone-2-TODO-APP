#!/usr/bin/env python3
"""Scaffold a new Next.js page with optional layout."""

import argparse
from pathlib import Path


def create_page(
    name: str,
    base_path: Path,
    with_layout: bool = False,
    with_loading: bool = False,
    with_error: bool = False,
    client: bool = False,
) -> None:
    """Create a new Next.js page structure."""

    app_path = base_path / "app"
    if not app_path.exists():
        print(f"Error: 'app' directory not found at {base_path}")
        return

    # Create page directory
    page_path = app_path / name
    page_path.mkdir(parents=True, exist_ok=True)
    print(f"Created: {page_path}")

    # Determine component name
    component_name = "".join(word.capitalize() for word in name.replace("/", " ").replace("-", " ").split())
    if not component_name:
        component_name = "Page"

    # Create page.tsx
    client_directive = "'use client';\n\n" if client else ""
    imports = "import { useState } from 'react';\n\n" if client else ""

    page_content = f'''{client_directive}{imports}export default function {component_name}Page() {{
  return (
    <div>
      <h1>{component_name}</h1>
      <p>Welcome to the {name} page.</p>
    </div>
  );
}}
'''

    page_file = page_path / "page.tsx"
    page_file.write_text(page_content)
    print(f"Created: {page_file}")

    # Create layout.tsx if requested
    if with_layout:
        layout_content = f'''export default function {component_name}Layout({{
  children,
}}: {{
  children: React.ReactNode;
}}) {{
  return (
    <section>
      <nav>
        {{/* {component_name} navigation */}}
      </nav>
      {{children}}
    </section>
  );
}}
'''
        layout_file = page_path / "layout.tsx"
        layout_file.write_text(layout_content)
        print(f"Created: {layout_file}")

    # Create loading.tsx if requested
    if with_loading:
        loading_content = f'''export default function {component_name}Loading() {{
  return (
    <div className="loading">
      <p>Loading...</p>
    </div>
  );
}}
'''
        loading_file = page_path / "loading.tsx"
        loading_file.write_text(loading_content)
        print(f"Created: {loading_file}")

    # Create error.tsx if requested
    if with_error:
        error_content = f''''use client';

export default function {component_name}Error({{
  error,
  reset,
}}: {{
  error: Error & {{ digest?: string }};
  reset: () => void;
}}) {{
  return (
    <div className="error">
      <h2>Something went wrong!</h2>
      <p>{{error.message}}</p>
      <button onClick={{() => reset()}}>Try again</button>
    </div>
  );
}}
'''
        error_file = page_path / "error.tsx"
        error_file.write_text(error_content)
        print(f"Created: {error_file}")

    print(f"\nPage '{name}' scaffolded successfully!")
    print(f"Route: /{name}")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new Next.js page"
    )
    parser.add_argument("name", help="Page name/path (e.g., 'dashboard' or 'blog/posts')")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Project root path (default: current directory)"
    )
    parser.add_argument(
        "--layout",
        action="store_true",
        help="Include layout.tsx"
    )
    parser.add_argument(
        "--loading",
        action="store_true",
        help="Include loading.tsx"
    )
    parser.add_argument(
        "--error",
        action="store_true",
        help="Include error.tsx"
    )
    parser.add_argument(
        "--client",
        action="store_true",
        help="Create as client component"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Include all files (layout, loading, error)"
    )

    args = parser.parse_args()

    with_layout = args.layout or args.full
    with_loading = args.loading or args.full
    with_error = args.error or args.full

    create_page(
        args.name,
        args.path,
        with_layout=with_layout,
        with_loading=with_loading,
        with_error=with_error,
        client=args.client,
    )


if __name__ == "__main__":
    main()
