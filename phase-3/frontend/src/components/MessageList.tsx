'use client'

import { Message, ToolCall } from '@/lib/api'

interface MessageListProps {
  messages: Message[]
}

function ToolCallDisplay({ toolCall }: { toolCall: ToolCall }) {
  return (
    <div className="mt-2 p-2 bg-gray-100 rounded text-xs">
      <div className="font-medium text-gray-600">
        Tool: {toolCall.name}
      </div>
      {Object.keys(toolCall.arguments).length > 0 && (
        <div className="text-gray-500 mt-1">
          Args: {JSON.stringify(toolCall.arguments)}
        </div>
      )}
    </div>
  )
}

export default function MessageList({ messages }: MessageListProps) {
  return (
    <div className="space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} message-enter`}
        >
          <div
            className={`max-w-[80%] rounded-2xl px-4 py-3 ${
              message.role === 'user'
                ? 'bg-blue-600 text-white rounded-br-md'
                : 'bg-white border border-gray-200 text-gray-800 rounded-bl-md shadow-sm'
            }`}
          >
            <p className="whitespace-pre-wrap">{message.content}</p>
            {message.toolCalls && message.toolCalls.length > 0 && (
              <div className="mt-2 border-t border-gray-200 pt-2">
                <div className="text-xs text-gray-500 mb-1">Actions performed:</div>
                {message.toolCalls.map((tc, idx) => (
                  <ToolCallDisplay key={idx} toolCall={tc} />
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
