'use client';

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
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent mb-4"></div>
          <p>Loading chat...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-red-600">
          <p className="font-semibold mb-2">Error loading chat</p>
          <p className="text-sm">{error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full">
      <ChatKit
        session={session}
        theme={{
          primaryColor: '#0066cc',
          fontFamily: 'system-ui, -apple-system, sans-serif',
          borderRadius: '0.5rem'
        }}
      />
    </div>
  );
}
