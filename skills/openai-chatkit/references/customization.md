# ChatKit Customization Guide

## Theme Customization

### Basic Theme Configuration

```typescript
<ChatKit
  session={session}
  theme={{
    primaryColor: '#0066cc',
    backgroundColor: '#ffffff',
    fontFamily: 'Inter, -apple-system, sans-serif'
  }}
/>
```

### Complete Theme Options

```typescript
theme: {
  // Colors
  primaryColor: string,           // Main brand color
  secondaryColor: string,         // Accent color
  backgroundColor: string,        // Main background
  surfaceColor: string,          // Card/panel backgrounds

  // Message styling
  userMessageBackground: string,  // User message bubbles
  userMessageColor: string,       // User message text
  botMessageBackground: string,   // Bot message bubbles
  botMessageColor: string,        // Bot message text

  // Typography
  fontFamily: string,             // Primary font
  fontSize: string,               // Base font size
  fontWeight: string | number,    // Font weight

  // Layout
  borderRadius: string,           // Corner roundness
  spacing: string,                // General spacing
  maxWidth: string,               // Chat container max width

  // Advanced
  shadowColor: string,            // Drop shadow color
  borderColor: string,            // Border colors
  inputBackground: string,        // Input field background
  buttonStyle: object             // Custom button styles
}
```

## Pre-built Theme Examples

### Professional Corporate Theme

```typescript
const corporateTheme = {
  primaryColor: '#1e40af',
  secondaryColor: '#3b82f6',
  backgroundColor: '#f9fafb',
  surfaceColor: '#ffffff',
  userMessageBackground: '#1e40af',
  userMessageColor: '#ffffff',
  botMessageBackground: '#e5e7eb',
  botMessageColor: '#111827',
  fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
  borderRadius: '0.5rem',
  spacing: '1rem'
};

<ChatKit session={session} theme={corporateTheme} />
```

### Modern Dark Mode

```typescript
const darkTheme = {
  primaryColor: '#60a5fa',
  secondaryColor: '#3b82f6',
  backgroundColor: '#111827',
  surfaceColor: '#1f2937',
  userMessageBackground: '#3b82f6',
  userMessageColor: '#ffffff',
  botMessageBackground: '#374151',
  botMessageColor: '#f3f4f6',
  fontFamily: 'system-ui, sans-serif',
  borderRadius: '0.75rem',
  borderColor: '#374151'
};
```

### Friendly Customer Support Theme

```typescript
const supportTheme = {
  primaryColor: '#10b981',
  secondaryColor: '#34d399',
  backgroundColor: '#ffffff',
  surfaceColor: '#f0fdf4',
  userMessageBackground: '#10b981',
  userMessageColor: '#ffffff',
  botMessageBackground: '#dcfce7',
  botMessageColor: '#14532d',
  fontFamily: '"Nunito", sans-serif',
  borderRadius: '1.5rem'
};
```

### Minimalist Theme

```typescript
const minimalistTheme = {
  primaryColor: '#000000',
  backgroundColor: '#ffffff',
  userMessageBackground: '#000000',
  userMessageColor: '#ffffff',
  botMessageBackground: '#f5f5f5',
  botMessageColor: '#000000',
  fontFamily: '"Helvetica Neue", sans-serif',
  fontSize: '15px',
  borderRadius: '4px',
  spacing: '0.75rem'
};
```

## Dynamic Theme Switching

### Light/Dark Mode Toggle

```tsx
function ThemeSwitcher() {
  const [isDark, setIsDark] = useState(false);

  const lightTheme = {
    primaryColor: '#2563eb',
    backgroundColor: '#ffffff',
    userMessageBackground: '#2563eb',
    botMessageBackground: '#f3f4f6'
  };

  const darkTheme = {
    primaryColor: '#60a5fa',
    backgroundColor: '#111827',
    userMessageBackground: '#3b82f6',
    botMessageBackground: '#374151'
  };

  const { session } = useChatKit({...});

  return (
    <>
      <button onClick={() => setIsDark(!isDark)}>
        {isDark ? '☀️' : '🌙'}
      </button>
      <ChatKit
        session={session}
        theme={isDark ? darkTheme : lightTheme}
      />
    </>
  );
}
```

### Brand Color Inheritance

```tsx
function BrandedChat() {
  const brandColors = {
    primary: getComputedStyle(document.documentElement)
      .getPropertyValue('--brand-primary'),
    secondary: getComputedStyle(document.documentElement)
      .getPropertyValue('--brand-secondary')
  };

  return (
    <ChatKit
      session={session}
      theme={{
        primaryColor: brandColors.primary,
        secondaryColor: brandColors.secondary,
        fontFamily: 'var(--font-family)',
        borderRadius: 'var(--border-radius)'
      }}
    />
  );
}
```

## Layout Customization

### Compact Layout

```tsx
<ChatKit
  session={session}
  layout={{
    compact: true,
    maxWidth: '400px',
    height: '500px',
    showHeader: false
  }}
  theme={{
    spacing: '0.5rem',
    fontSize: '14px'
  }}
/>
```

### Full-Screen Layout

```tsx
<div className="h-screen w-screen">
  <ChatKit
    session={session}
    layout={{
      fullscreen: true,
      showHeader: true,
      headerTitle: "AI Assistant"
    }}
  />
</div>
```

### Sidebar Layout

```css
.chat-sidebar {
  position: fixed;
  right: 0;
  top: 0;
  width: 400px;
  height: 100vh;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
}
```

```tsx
<div className="chat-sidebar">
  <ChatKit
    session={session}
    theme={{
      maxWidth: '100%',
      backgroundColor: '#f9fafb'
    }}
  />
</div>
```

## Component Customization

### Custom Header

```tsx
<ChatKit
  session={session}
  components={{
    header: () => (
      <div className="custom-header">
        <img src="/logo.png" alt="Logo" />
        <h2>Support Chat</h2>
        <button onClick={handleClose}>×</button>
      </div>
    )
  }}
/>
```

### Custom Input Field

```tsx
<ChatKit
  session={session}
  components={{
    input: (props) => (
      <div className="custom-input">
        <textarea
          {...props}
          placeholder="Ask me anything..."
          className="custom-textarea"
        />
        <button type="submit">Send</button>
      </div>
    )
  }}
/>
```

### Custom Message Bubbles

```tsx
<ChatKit
  session={session}
  components={{
    userMessage: (message) => (
      <div className="user-bubble">
        <span>{message.content}</span>
        <time>{formatTime(message.timestamp)}</time>
      </div>
    ),
    botMessage: (message) => (
      <div className="bot-bubble">
        <Avatar src="/bot-avatar.png" />
        <div className="message-content">
          {message.content}
        </div>
      </div>
    )
  }}
/>
```

## Branding Elements

### Logo Integration

```tsx
<ChatKit
  session={session}
  branding={{
    logo: '/company-logo.svg',
    logoAlt: 'Company Name',
    showPoweredBy: false
  }}
/>
```

### Custom Welcome Message

```tsx
<ChatKit
  session={session}
  config={{
    welcomeMessage: {
      title: "Welcome to Support Chat!",
      subtitle: "How can we help you today?",
      avatar: "/support-avatar.png",
      quickActions: [
        { label: "Track Order", action: "track_order" },
        { label: "Return Item", action: "return_item" },
        { label: "Contact Human", action: "escalate" }
      ]
    }
  }}
/>
```

### Custom Empty State

```tsx
<ChatKit
  session={session}
  components={{
    emptyState: () => (
      <div className="empty-state">
        <img src="/chat-illustration.svg" />
        <h3>Start a conversation</h3>
        <p>Ask me anything about our products!</p>
      </div>
    )
  }}
/>
```

## Internationalization

### Multi-language Support

```tsx
const translations = {
  en: {
    placeholder: 'Type your message...',
    send: 'Send',
    thinking: 'Thinking...',
    error: 'Something went wrong'
  },
  es: {
    placeholder: 'Escribe tu mensaje...',
    send: 'Enviar',
    thinking: 'Pensando...',
    error: 'Algo salió mal'
  }
};

function LocalizedChat({ locale = 'en' }) {
  return (
    <ChatKit
      session={session}
      locale={locale}
      translations={translations[locale]}
    />
  );
}
```

## Accessibility Customization

### ARIA Labels and Keyboard Navigation

```tsx
<ChatKit
  session={session}
  accessibility={{
    ariaLabel: 'Customer support chat',
    announceMessages: true,
    keyboardShortcuts: {
      send: 'Enter',
      newLine: 'Shift+Enter',
      close: 'Escape'
    }
  }}
/>
```

### High Contrast Mode

```typescript
const highContrastTheme = {
  primaryColor: '#0000ff',
  backgroundColor: '#ffffff',
  userMessageBackground: '#000000',
  userMessageColor: '#ffffff',
  botMessageBackground: '#ffffff',
  botMessageColor: '#000000',
  borderColor: '#000000',
  borderWidth: '2px'
};
```

## Animation Customization

### Message Animation

```tsx
<ChatKit
  session={session}
  animations={{
    messageEntry: 'slide-up',
    typingIndicator: 'pulse',
    duration: '200ms',
    easing: 'ease-out'
  }}
/>
```

### Disable Animations

```tsx
<ChatKit
  session={session}
  animations={{
    enabled: false
  }}
/>
```

## Mobile Optimization

### Responsive Theme

```tsx
const responsiveTheme = {
  primaryColor: '#2563eb',
  fontFamily: 'system-ui',
  fontSize: window.innerWidth < 768 ? '14px' : '16px',
  spacing: window.innerWidth < 768 ? '0.5rem' : '1rem',
  borderRadius: window.innerWidth < 768 ? '1rem' : '0.5rem'
};
```

### Mobile-Specific Layout

```tsx
function ResponsiveChat() {
  const isMobile = useMediaQuery('(max-width: 768px)');

  return (
    <ChatKit
      session={session}
      layout={{
        fullscreen: isMobile,
        maxWidth: isMobile ? '100%' : '600px'
      }}
    />
  );
}
```

## CSS Custom Properties

### Using CSS Variables

```css
:root {
  --chatkit-primary: #2563eb;
  --chatkit-bg: #ffffff;
  --chatkit-user-msg-bg: #2563eb;
  --chatkit-bot-msg-bg: #f3f4f6;
  --chatkit-font: 'Inter', sans-serif;
  --chatkit-radius: 0.5rem;
}

.dark-mode {
  --chatkit-primary: #60a5fa;
  --chatkit-bg: #111827;
  --chatkit-user-msg-bg: #3b82f6;
  --chatkit-bot-msg-bg: #374151;
}
```

```tsx
<ChatKit
  session={session}
  theme={{
    primaryColor: 'var(--chatkit-primary)',
    backgroundColor: 'var(--chatkit-bg)',
    userMessageBackground: 'var(--chatkit-user-msg-bg)',
    botMessageBackground: 'var(--chatkit-bot-msg-bg)',
    fontFamily: 'var(--chatkit-font)',
    borderRadius: 'var(--chatkit-radius)'
  }}
/>
```

## Best Practices

1. **Maintain brand consistency** - Use your company's design system
2. **Test in multiple contexts** - Light/dark mode, different screen sizes
3. **Consider accessibility** - High contrast, keyboard navigation, screen readers
4. **Keep it simple** - Don't over-customize at the expense of usability
5. **Use CSS variables** - Makes theme switching easier
6. **Test on real devices** - Mobile behavior can differ from desktop
7. **Performance matters** - Avoid heavy animations or large assets
8. **Provide fallbacks** - Handle cases where custom fonts/assets fail to load
