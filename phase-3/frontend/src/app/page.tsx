'use client'

import { useState } from 'react'
import ChatInterface from '@/components/ChatInterface'

export default function Home() {
  const [userId, setUserId] = useState<string>('')
  const [isStarted, setIsStarted] = useState(false)

  const handleStart = (e: React.FormEvent) => {
    e.preventDefault()
    if (userId.trim()) {
      setIsStarted(true)
    }
  }

  if (!isStarted) {
    return (
      <main className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              Todo AI Chatbot
            </h1>
            <p className="text-gray-600">
              Manage your tasks through natural conversation
            </p>
          </div>

          <form onSubmit={handleStart} className="space-y-4">
            <div>
              <label
                htmlFor="userId"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Enter your User ID
              </label>
              <input
                type="text"
                id="userId"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                placeholder="e.g., john_doe"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              />
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!userId.trim()}
            >
              Start Chatting
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-500">
            <p>Try saying things like:</p>
            <ul className="mt-2 space-y-1">
              <li>&quot;Add a task to buy groceries&quot;</li>
              <li>&quot;Show me my tasks&quot;</li>
              <li>&quot;Mark task 1 as done&quot;</li>
            </ul>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen">
      <ChatInterface userId={userId} onLogout={() => setIsStarted(false)} />
    </main>
  )
}
