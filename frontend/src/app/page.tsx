"use client";

import { useState, useEffect, useMemo, useCallback, memo } from "react";
import { useTasks, Task } from "../lib/hooks/useTasks";
import { authClient } from "../lib/auth-client";
import { ChatBubble } from "../components/ChatBubble";

// Icons as inline SVGs for a clean look
const PlusIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"></line>
    <line x1="5" y1="12" x2="19" y2="12"></line>
  </svg>
);

const TrashIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6"></polyline>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
    <line x1="10" y1="11" x2="10" y2="17"></line>
    <line x1="14" y1="11" x2="14" y2="17"></line>
  </svg>
);

const EditIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
  </svg>
);

const SaveIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
);

const CancelIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
);

const CheckCircleIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
    <polyline points="22 4 12 14.01 9 11.01"></polyline>
  </svg>
);

const LogOutIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
    <polyline points="16 17 21 12 16 7"></polyline>
    <line x1="21" y1="12" x2="9" y2="12"></line>
  </svg>
);

const LoaderIcon = () => (
  <svg className="animate-spin" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="2" x2="12" y2="6"></line>
    <line x1="12" y1="18" x2="12" y2="22"></line>
    <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
    <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
    <line x1="2" y1="12" x2="6" y2="12"></line>
    <line x1="18" y1="12" x2="22" y2="12"></line>
    <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
    <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
  </svg>
);

const MailIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="4" width="20" height="16" rx="2"></rect>
    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
  </svg>
);

const LockIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
  </svg>
);

const UserIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
);

// Loading skeleton component
const TaskSkeleton = () => (
  <div className="flex items-center gap-2 sm:gap-4 p-3 sm:p-4 rounded-lg sm:rounded-xl bg-[var(--card)] border border-[var(--card-border)] animate-pulse">
    <div className="w-5 h-5 sm:w-6 sm:h-6 rounded-md bg-[var(--input-bg)]"></div>
    <div className="flex-1 h-4 sm:h-5 rounded bg-[var(--input-bg)]"></div>
    <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-[var(--input-bg)]"></div>
  </div>
);

// Empty state component
const EmptyState = () => (
  <div className="flex flex-col items-center justify-center py-10 sm:py-16 text-center animate-fade-in px-4">
    <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-[var(--primary-light)] flex items-center justify-center mb-4 sm:mb-6">
      <CheckCircleIcon />
    </div>
    <h3 className="text-lg sm:text-xl font-semibold mb-2">No tasks yet</h3>
    <p className="text-[var(--muted)] max-w-sm text-sm sm:text-base">
      Start by adding your first task above. Stay organized and get things done!
    </p>
  </div>
);

// Task item component - memoized to prevent unnecessary re-renders
interface TaskItemProps {
  task: Task;
  onToggle: (id: number) => void;
  onEdit: (id: number, content: string) => void;
  onDelete: (id: number) => void;
}

const TaskItem = memo(function TaskItem({
  task,
  onToggle,
  onEdit,
  onDelete
}: TaskItemProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(task.content);

  const handleDelete = async () => {
    setIsDeleting(true);
    await onDelete(task.id);
  };

  const handleSave = async () => {
    if (editContent.trim() && editContent !== task.content) {
      await onEdit(task.id, editContent.trim());
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditContent(task.content);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  return (
    <div
      className={`
        group flex items-center gap-2 sm:gap-4 p-3 sm:p-4 rounded-lg sm:rounded-xl
        bg-[var(--card)] border border-[var(--card-border)]
        hover:shadow-[var(--shadow)] transition-all duration-200
        animate-slide-in
        ${task.completed ? 'opacity-70' : ''}
        ${isDeleting ? 'opacity-50 scale-95' : ''}
      `}
    >
      <input
        type="checkbox"
        checked={task.completed}
        onChange={() => onToggle(task.id)}
        className="custom-checkbox w-5 h-5 sm:w-6 sm:h-6"
        disabled={isEditing}
      />
      {isEditing ? (
        <input
          type="text"
          value={editContent}
          onChange={(e) => setEditContent(e.target.value)}
          onKeyDown={handleKeyDown}
          autoFocus
          className="
            flex-1 px-2 sm:px-3 py-1 rounded-lg text-sm sm:text-base
            bg-[var(--input-bg)] border border-[var(--primary)]
            focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/20
            transition-all duration-200
          "
        />
      ) : (
        <span
          className={`
            flex-1 text-sm sm:text-base transition-all duration-200 cursor-pointer break-words
            ${task.completed ? 'line-through text-[var(--muted)]' : ''}
          `}
          onDoubleClick={() => !task.completed && setIsEditing(true)}
          title="Double-click to edit"
        >
          {task.content}
        </span>
      )}
      <div className="flex items-center gap-0.5 sm:gap-1 flex-shrink-0">
        {isEditing ? (
          <>
            <button
              onClick={handleSave}
              className="
                p-1.5 sm:p-2 rounded-lg text-[var(--success)]
                hover:bg-[var(--success)]/10
                transition-all duration-200
              "
              title="Save"
            >
              <SaveIcon />
            </button>
            <button
              onClick={handleCancel}
              className="
                p-1.5 sm:p-2 rounded-lg text-[var(--muted)]
                hover:text-[var(--danger)] hover:bg-[var(--danger)]/10
                transition-all duration-200
              "
              title="Cancel"
            >
              <CancelIcon />
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => setIsEditing(true)}
              disabled={task.completed}
              className="
                opacity-100 sm:opacity-0 sm:group-hover:opacity-100
                p-1.5 sm:p-2 rounded-lg text-[var(--muted)]
                hover:text-[var(--primary)] hover:bg-[var(--primary)]/10
                transition-all duration-200
                disabled:opacity-30 disabled:cursor-not-allowed
              "
              title="Edit task"
            >
              <EditIcon />
            </button>
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="
                opacity-100 sm:opacity-0 sm:group-hover:opacity-100
                p-1.5 sm:p-2 rounded-lg text-[var(--muted)]
                hover:text-[var(--danger)] hover:bg-[var(--danger)]/10
                transition-all duration-200
                disabled:opacity-50
              "
              title="Delete task"
            >
              <TrashIcon />
            </button>
          </>
        )}
      </div>
    </div>
  );
});

// Stats component - memoized to prevent unnecessary re-renders
const TaskStats = memo(function TaskStats({ tasks }: { tasks: Task[] }) {
  const total = tasks.length;
  const completed = tasks.filter(t => t.completed).length;
  const pending = total - completed;
  const progress = total > 0 ? (completed / total) * 100 : 0;

  return (
    <div className="grid grid-cols-3 gap-2 sm:gap-4 mb-6 sm:mb-8 animate-fade-in">
      <div className="bg-[var(--card)] border border-[var(--card-border)] rounded-lg sm:rounded-xl p-2 sm:p-4 text-center">
        <div className="text-xl sm:text-3xl font-bold text-[var(--primary)]">{total}</div>
        <div className="text-xs sm:text-sm text-[var(--muted)]">Total</div>
      </div>
      <div className="bg-[var(--card)] border border-[var(--card-border)] rounded-lg sm:rounded-xl p-2 sm:p-4 text-center">
        <div className="text-xl sm:text-3xl font-bold text-[var(--success)]">{completed}</div>
        <div className="text-xs sm:text-sm text-[var(--muted)]">Done</div>
      </div>
      <div className="bg-[var(--card)] border border-[var(--card-border)] rounded-lg sm:rounded-xl p-2 sm:p-4 text-center">
        <div className="text-xl sm:text-3xl font-bold text-[var(--secondary)]">{pending}</div>
        <div className="text-xs sm:text-sm text-[var(--muted)]">Pending</div>
      </div>
      {total > 0 && (
        <div className="col-span-3 bg-[var(--card)] border border-[var(--card-border)] rounded-lg sm:rounded-xl p-3 sm:p-4">
          <div className="flex justify-between text-xs sm:text-sm mb-2">
            <span className="text-[var(--muted)]">Progress</span>
            <span className="font-medium">{Math.round(progress)}%</span>
          </div>
          <div className="h-1.5 sm:h-2 bg-[var(--input-bg)] rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-[var(--primary)] to-[var(--success)] rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      )}
    </div>
  );
});

// Sign in/up page component
const AuthPage = ({ onAuthSuccess }: { onAuthSuccess?: () => Promise<void> }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      if (isSignUp) {
        const result = await authClient.signUp.email({
          email,
          password,
          name,
        });

        if (result.error) {
          const errorMsg = result.error.message || String(result.error.status) || "Sign up failed. Database may be waking up, please try again in 30 seconds.";
          setError(errorMsg);
          setIsLoading(false);
        } else if (!result.data) {
          setError("Sign up failed - no response from server. Database may still be waking up. Wait 30 seconds and try again.");
          setIsLoading(false);
        } else {
          await onAuthSuccess?.();
        }
      } else {
        const result = await authClient.signIn.email({
          email,
          password,
        });

        if (result.error) {
          const errorMsg = result.error.message || String(result.error.status) || "Sign in failed. Database may be waking up, please try again.";
          setError(errorMsg);
          setIsLoading(false);
        } else if (!result.data) {
          setError("Sign in failed - no response from server. Database may still be waking up.");
          setIsLoading(false);
        } else {
          await onAuthSuccess?.();
        }
      }
    } catch {
      setError("Authentication failed. Please try again.");
      setIsLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await authClient.signIn.social({ provider: "google" });
    } catch {
      setError("Google sign-in is not configured. Please use email/password.");
      setIsLoading(false);
    }
  };

  const handleGithubSignIn = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await authClient.signIn.social({ provider: "github" });
    } catch {
      setError("GitHub sign-in is not configured. Please use email/password.");
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-6 bg-gradient-to-br from-[var(--background)] to-[var(--primary-light)]">
      <div className="w-full max-w-md animate-fade-in">
        <div className="bg-[var(--card)] border border-[var(--card-border)] rounded-xl sm:rounded-2xl shadow-[var(--shadow-lg)] p-5 sm:p-8">
          {/* Logo & Title */}
          <div className="text-center mb-6 sm:mb-8">
            <div className="rounded-xl flex items-center justify-center mx-auto mb-3 sm:mb-4 shadow-lg overflow-hidden">
              <img src="/logo.png" alt="Q.TODO App Logo" style={{ width: '56px', height: '56px' }} className="sm:w-[80px] sm:h-[80px] object-contain rounded-xl" />
            </div>
            <h1 className="text-xl sm:text-2xl font-bold mb-1 sm:mb-2">
              {isSignUp ? "Create Account" : "Welcome Back"}
            </h1>
            <p className="text-[var(--muted)] text-sm sm:text-base">
              {isSignUp ? "Sign up to start managing your tasks" : "Sign in to manage your tasks"}
            </p>
          </div>

          {/* Error message */}
          {error && (
            <div className="bg-[var(--danger)]/10 border border-[var(--danger)]/20 rounded-xl p-3 mb-6 text-[var(--danger)] text-sm animate-fade-in">
              {error}
            </div>
          )}

          {/* Email/Password Form */}
          <form onSubmit={handleEmailAuth} className="space-y-3 sm:space-y-4 mb-5 sm:mb-6">
            {isSignUp && (
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center text-[var(--muted)]">
                  <UserIcon />
                </div>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Full name"
                  required={isSignUp}
                  className="
                    w-full pl-10 pr-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl text-sm sm:text-base
                    bg-[var(--input-bg)] border border-[var(--card-border)]
                    focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20 focus:shadow-md
                    transition-all duration-200
                    placeholder:text-[var(--muted)]
                  "
                />
              </div>
            )}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center text-[var(--muted)]">
                <MailIcon />
              </div>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email address"
                required
                className="
                  w-full pl-10 pr-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl text-sm sm:text-base
                  bg-[var(--input-bg)] border border-[var(--card-border)]
                  focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20 focus:shadow-md
                  transition-all duration-200
                  placeholder:text-[var(--muted)]
                "
              />
            </div>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center text-[var(--muted)]">
                <LockIcon />
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                required
                minLength={8}
                className="
                  w-full pl-10 pr-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl text-sm sm:text-base
                  bg-[var(--input-bg)] border border-[var(--card-border)]
                  focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20 focus:shadow-md
                  transition-all duration-200
                  placeholder:text-[var(--muted)]
                "
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="
                w-full py-2.5 sm:py-3 rounded-lg sm:rounded-xl font-medium text-sm sm:text-base
                bg-gradient-to-r from-[var(--primary)] to-[var(--primary-hover)]
                text-white
                hover:shadow-lg hover:shadow-[var(--primary)]/25
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-200
                flex items-center justify-center gap-2
              "
            >
              {isLoading ? <LoaderIcon /> : null}
              {isSignUp ? "Create Account" : "Sign In"}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-5 sm:my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[var(--card-border)]"></div>
            </div>
            <div className="relative flex justify-center text-xs sm:text-sm">
              <span className="px-3 sm:px-4 bg-[var(--card)] text-[var(--muted)]">or continue with</span>
            </div>
          </div>

          {/* Social sign in buttons */}
          <div className="grid grid-cols-2 gap-2 sm:gap-3">
            <button
              onClick={handleGoogleSignIn}
              disabled={isLoading}
              className="
                flex items-center justify-center gap-1.5 sm:gap-2
                px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl border border-[var(--card-border)]
                bg-[var(--card)] text-[var(--foreground)] hover:bg-[var(--input-bg)]
                transition-all duration-200 font-medium text-xs sm:text-sm
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            >
              <svg width="16" height="16" className="sm:w-[18px] sm:h-[18px]" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Google
            </button>

            <button
              onClick={handleGithubSignIn}
              disabled={isLoading}
              className="
                flex items-center justify-center gap-1.5 sm:gap-2
                px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl border border-[var(--card-border)]
                bg-[var(--card)] text-[var(--foreground)] hover:bg-[var(--input-bg)]
                transition-all duration-200 font-medium text-xs sm:text-sm
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            >
              <svg width="16" height="16" className="sm:w-[18px] sm:h-[18px]" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              GitHub
            </button>
          </div>

          {/* Toggle sign in/up */}
          <p className="text-center text-xs sm:text-sm text-[var(--muted)] mt-5 sm:mt-6">
            {isSignUp ? "Already have an account?" : "Don't have an account?"}{" "}
            <button
              onClick={() => {
                setIsSignUp(!isSignUp);
                setError(null);
              }}
              className="text-[var(--primary)] hover:underline font-medium"
            >
              {isSignUp ? "Sign in" : "Sign up"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

// Loading screen component
const LoadingScreen = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="text-center animate-fade-in">
      <div className="rounded-xl flex items-center justify-center mx-auto mb-4 animate-pulse overflow-hidden">
        <img src="/logo.png" alt="Q.TODO App Logo" style={{ width: '80px', height: '80px' }} className="object-contain rounded-xl" />
      </div>
      <p className="text-[var(--muted)]">Loading...</p>
    </div>
  </div>
);

// Main app component
export default function Home() {
  const { data: session, isPending, error } = authClient.useSession();
  const user = session?.user;
  const ready = !isPending;

  const [newTaskContent, setNewTaskContent] = useState("");
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");

  // Pass session data in the format expected by useTasks
  // Note: token is fetched separately in useTasks via /api/auth/token endpoint
  const sessionData = user ? {
    user: {
      id: user.id,
      email: user.email,
      name: user.name,
      image: user.image,
    },
  } : null;

  const { tasks, loading: tasksLoading, error: tasksError, addTask, updateTask, toggleComplete, deleteTask, refetch } = useTasks(sessionData);
  const [jwtToken, setJwtToken] = useState<string | null>(null);

  // Fetch JWT token for chat
  useEffect(() => {
    async function getToken() {
      if (user) {
        try {
          const url = `${process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"}/api/auth/token`;
          const response = await fetch(url, {
            credentials: "include",
          });
          if (response.ok) {
            const data = await response.json();
            setJwtToken(data.token || null);
          } else {
            setJwtToken(null);
          }
        } catch {
          setJwtToken(null);
        }
      } else {
        setJwtToken(null);
      }
    }
    getToken();
  }, [user]);

  const handleAddTask = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskContent.trim()) return;
    await addTask(newTaskContent);
    setNewTaskContent("");
  }, [newTaskContent, addTask]);

  const handleSignOut = useCallback(async () => {
    await authClient.signOut();
  }, []);

  // Memoize filtered tasks to prevent recalculation on every render
  const filteredTasks = useMemo(() => {
    return tasks.filter(task => {
      if (filter === "active") return !task.completed;
      if (filter === "completed") return task.completed;
      return true;
    });
  }, [tasks, filter]);

  if (!ready) {
    return <LoadingScreen />;
  }

  // Handle auth success by refetching session
  const handleAuthSuccess = async () => {
    window.location.reload();
  };

  if (!user) {
    return <AuthPage onAuthSuccess={handleAuthSuccess} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[var(--background)] to-[var(--primary-light)]/30">
      {/* Header */}
      <header className="bg-[var(--card)]/80 backdrop-blur-md border-b border-[var(--card-border)] sticky top-0 z-50 shadow-lg">
        <div className="max-w-2xl mx-auto px-3 sm:px-6 py-3 sm:py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="rounded-lg flex items-center justify-center overflow-hidden">
              <img src="/logo.png" alt="Q.TODO App Logo" style={{ width: '36px', height: '36px' }} className="sm:w-[44px] sm:h-[44px] object-contain rounded-lg" />
            </div>
            <h1 className="text-lg sm:text-xl font-bold">Q.TODO App</h1>
          </div>
          <div className="flex items-center gap-2 sm:gap-4">
            <div className="flex items-center gap-2">
              {user.image ? (
                <img
                  src={user.image}
                  alt={user.name || "User"}
                  className="w-7 h-7 sm:w-8 sm:h-8 rounded-full"
                />
              ) : (
                <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-[var(--primary)] flex items-center justify-center text-white text-xs sm:text-sm font-medium transition-all duration-200">
                  {user.name?.charAt(0) || user.email?.charAt(0) || "U"}
                </div>
              )}
              <span className="text-xs sm:text-sm font-medium hidden sm:block max-w-[120px] truncate">{user.name || user.email}</span>
            </div>
            <button
              onClick={handleSignOut}
              className="p-1.5 sm:p-2 rounded-lg text-[var(--muted)] hover:text-[var(--danger)] hover:bg-[var(--danger)]/10 transition-all duration-200"
              title="Sign out"
            >
              <LogOutIcon />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-3 sm:px-6 py-4 sm:py-8">
        {/* Stats */}
        {tasks.length > 0 && <TaskStats tasks={tasks} />}

        {/* Add Task Form */}
        <form onSubmit={handleAddTask} className="mb-6 sm:mb-8 animate-fade-in">
          <div className="flex gap-2 sm:gap-3">
            <input
              type="text"
              value={newTaskContent}
              onChange={(e) => setNewTaskContent(e.target.value)}
              placeholder="What needs to be done?"
              className="
                flex-1 px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl text-sm sm:text-base
                bg-[var(--card)] border border-[var(--card-border)]
                focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20 focus:shadow-md
                transition-all duration-200
                placeholder:text-[var(--muted)]
              "
            />
            <button
              type="submit"
              disabled={!newTaskContent.trim() || tasksLoading}
              className="
                px-3 sm:px-5 py-2.5 sm:py-3 rounded-lg sm:rounded-xl
                bg-gradient-to-r from-[var(--primary)] to-[var(--primary-hover)]
                text-white font-medium
                hover:shadow-lg hover:shadow-[var(--primary)]/25
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-200
                flex items-center gap-2
              "
            >
              {tasksLoading ? <LoaderIcon /> : <PlusIcon />}
              <span className="hidden sm:inline">Add Task</span>
            </button>
          </div>
        </form>

        {/* Filter Tabs */}
        {tasks.length > 0 && (
          <div className="flex gap-1.5 sm:gap-2 mb-4 sm:mb-6 animate-fade-in overflow-x-auto pb-1">
            {(["all", "active", "completed"] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`
                  px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg sm:rounded-xl text-xs sm:text-sm font-medium whitespace-nowrap
                  transition-all duration-200
                  ${filter === f
                    ? 'bg-[var(--primary)] text-white'
                    : 'bg-[var(--card)] border border-[var(--card-border)] hover:border-[var(--primary)]'
                  }
                `}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        )}

        {/* Error State */}
        {tasksError && (
          <div className="bg-[var(--danger)]/10 border border-[var(--danger)]/20 rounded-lg sm:rounded-xl p-3 sm:p-4 mb-4 sm:mb-6 text-[var(--danger)] text-sm sm:text-base animate-fade-in">
            {tasksError}
          </div>
        )}

        {/* Task List */}
        <div className="space-y-2 sm:space-y-3">
          {tasksLoading && tasks.length === 0 ? (
            <>
              <TaskSkeleton />
              <TaskSkeleton />
              <TaskSkeleton />
            </>
          ) : filteredTasks.length === 0 && tasks.length === 0 ? (
            <EmptyState />
          ) : filteredTasks.length === 0 ? (
            <div className="text-center py-6 sm:py-8 text-sm sm:text-base text-[var(--muted)] animate-fade-in">
              No {filter} tasks
            </div>
          ) : (
            filteredTasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onToggle={toggleComplete}
                onEdit={updateTask}
                onDelete={deleteTask}
              />
            ))
          )}
        </div>

        {/* Clear completed button */}
        {tasks.some(t => t.completed) && (
          <div className="mt-6 sm:mt-8 text-center animate-fade-in">
            <button
              onClick={() => {
                tasks.filter(t => t.completed).forEach(t => deleteTask(t.id));
              }}
              className="text-xs sm:text-sm text-[var(--muted)] hover:text-[var(--danger)] transition-colors py-2 px-4"
            >
              Clear completed tasks
            </button>
          </div>
        )}
      </main>


      {/* AI Chat Assistant */}
      {jwtToken && (
        <ChatBubble
          userId={user.id}
          token={jwtToken}
          onTasksChanged={refetch}
        />
      )}
    </div>
  );
}
