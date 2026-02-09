---
name: gemini-nextjs-toolkit
description: This skill provides tools and guidance for developing Next.js applications that leverage Gemini models for advanced AI capabilities. Use this skill when building modern web applications requiring features like intelligent content generation, natural language understanding, personalized user experiences, and task automation.
---

# Gemini Next.js Toolkit

## Overview

This skill provides a foundation and set of guidelines for integrating Gemini models into Next.js applications, enabling the creation of dynamic, intelligent, and user-centric web experiences. It facilitates development of applications that are both "affective" (understanding and responding to user sentiment/context) and "productive" (automating tasks, generating content, assisting users).

## Quick Start: Using the Next.js Template

To quickly scaffold a new Next.js project pre-configured for Gemini model integration, use the provided template:

1.  **Copy the template:**
    ```bash
    cp -R ./gemini-nextjs-toolkit/assets/nextjs-template <your-project-name>
    cd <your-project-name>
    ```
    *Note: On Windows, use `xcopy /E /I .\gemini-nextjs-toolkit\assets\nextjs-template .\<your-project-name>` then `cd <your-project-name>`.*
2.  **Install dependencies:**
    ```bash
    npm install
    # or yarn install
    # or pnpm install
    ```
3.  **Start the development server:**
    ```bash
    npm run dev
    ```
    Your new Next.js application will be running at `http://localhost:3000`.

## Integrating Gemini Models

This skill promotes a flexible approach to integrating Gemini models, typically involving:

1.  **Backend API:** For secure and efficient interaction with Gemini models, it's recommended to set up a simple backend API (e.g., using Node.js, Python FastAPI) that handles API key management and direct calls to the Gemini API.
2.  **Frontend Interaction:** The Next.js frontend will then communicate with your backend API to send user prompts and receive model responses.

## Building Affective & Productive Applications

*   **Affective:**
    *   Implement sentiment analysis on user input to tailor responses.
    *   Personalize content and recommendations based on user history and preferences.
    *   Design conversational interfaces that understand context and emotional cues.
*   **Productive:**
    *   Automate content creation (e.g., articles, social media posts).
    *   Summarize lengthy documents or conversations.
    *   Generate code snippets or provide programming assistance.
    *   Facilitate complex task automation through natural language commands.

## Resources

This skill includes various resources to aid in development:

### scripts/
Executable code that can be run directly to perform specific operations. (e.g., scripts for setting up backend API proxies, utility functions for data processing).

### references/
Documentation and reference material intended to be loaded into context to inform Gemini CLI's process and thinking. (e.g., detailed guides for specific Gemini API calls, best practices for prompt engineering, examples of affective computing patterns).

### assets/
Files not intended to be loaded into context, but rather used within the output Gemini CLI produces.

*   `nextjs-template/`: A basic Next.js project template to kickstart development.

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
