# viewer_lighting.js

## Overview

This file contains the **Twemoji emoji library** - NOT 3D lighting code. Twemoji converts emoji characters to Twitter's emoji images for consistent cross-platform display.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~91KB (minified)
- **Type**: Emoji parsing library
- **Library**: Twemoji (twitter/twemoji)

## Purpose

Sketchfab uses Twemoji to ensure emojis display consistently across all browsers and operating systems, replacing system emojis with Twitter's emoji images.

## Core Functions

### 1. Parse String

```javascript
// Basic usage
const html = twemoji.parse('Hello 👋 World! 🌍');
// Output: 'Hello <img class="emoji" src="..."> World! <img class="emoji" src="...">'

// With options
twemoji.parse(text, {
  base: 'https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/',
  folder: 'svg',
  ext: '.svg',
  className: 'custom-emoji',
  callback: (icon, options) => {
    // Custom URL generation
    return `${options.base}${options.folder}/${icon}${options.ext}`;
  }
});
```

### 2. Parse DOM

```javascript
// Parse all text in a DOM element
twemoji.parse(document.body);

// Parse specific element
const element = document.getElementById('comments');
twemoji.parse(element);
```

### 3. Get Emoji URL

```javascript
// Get URL for a specific emoji
const url = twemoji.parse('🚀', { 
  callback: (icon, options) => `${options.base}svg/${icon}.svg` 
});
```

## Options

```javascript
const defaultOptions = {
  // CDN base URL
  base: 'https://twemoji.maxcdn.com/v/latest/',
  
  // Asset folder ('72x72' for PNG, 'svg' for SVG)
  folder: '72x72',
  
  // File extension
  ext: '.png',
  
  // CSS class for img elements
  className: 'emoji',
  
  // Custom callback for URL generation
  callback: (icon, options) => {
    return `${options.base}${options.folder}/${icon}${options.ext}`;
  },
  
  // Attributes for img elements
  attributes: () => ({
    loading: 'lazy'
  })
};
```

## Unicode Regex

The library includes comprehensive regex patterns for emoji detection:

```javascript
// Matches all emoji sequences including:
// - Basic emoji: 😀
// - Emoji with skin tone: 👋🏽
// - Emoji ZWJ sequences: 👨‍👩‍👧‍👦
// - Flag sequences: 🇺🇸
// - Keycap sequences: 1️⃣

const emojiRegex = /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|.../gu;
```

## Output Format

### HTML Output

```html
<!-- Input: "Hello 👋" -->
<!-- Output: -->
Hello <img 
  class="emoji" 
  draggable="false" 
  alt="👋" 
  src="https://twemoji.maxcdn.com/v/latest/72x72/1f44b.png"
>
```

### SVG Output (with folder: 'svg')

```html
Hello <img 
  class="emoji" 
  draggable="false" 
  alt="👋" 
  src="https://twemoji.maxcdn.com/v/latest/svg/1f44b.svg"
>
```

## Integration with Sketchfab

### Comment Rendering

```javascript
// Used in comment system
const renderComment = (text) => {
  const escaped = escapeHtml(text);
  return twemoji.parse(escaped, {
    className: 'comment-emoji',
    folder: 'svg',
    ext: '.svg'
  });
};
```

### User Display Names

```javascript
// User names with emojis
const displayName = twemoji.parse(user.displayName);
```

### Model Descriptions

```javascript
// Model descriptions with emojis
const description = twemoji.parse(model.description, {
  className: 'description-emoji'
});
```

## CSS Styling

```css
/* Default emoji styling */
.emoji {
  height: 1em;
  width: 1em;
  margin: 0 0.05em 0 0.1em;
  vertical-align: -0.1em;
}

/* Larger emoji for titles */
.title .emoji {
  height: 1.2em;
  width: 1.2em;
}

/* Custom class */
.comment-emoji {
  height: 1.1em;
  width: 1.1em;
  vertical-align: -0.15em;
}
```

## HTML Entity Escaping

Built-in HTML escaping for security:

```javascript
// Internal escaping function
const escapeHtml = (text) => {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
};
```

## Performance Considerations

```javascript
// Efficient parsing for large documents
twemoji.parse(element, {
  // Use SVG for better quality at all sizes
  folder: 'svg',
  ext: '.svg',
  
  // Add lazy loading
  attributes: () => ({ loading: 'lazy' }),
  
  // Skip certain elements
  callback: (icon, options, variant) => {
    // Return false to skip
    if (shouldSkip(icon)) return false;
    return `${options.base}svg/${icon}.svg`;
  }
});
```

## Usage Examples

### React Component

```jsx
function EmojiText({ text }) {
  const ref = useRef();
  
  useEffect(() => {
    if (ref.current) {
      twemoji.parse(ref.current, {
        folder: 'svg',
        ext: '.svg'
      });
    }
  }, [text]);
  
  return <span ref={ref}>{text}</span>;
}
```

### Comment System

```jsx
function Comment({ comment }) {
  const htmlContent = useMemo(() => {
    const escaped = escapeHtml(comment.text);
    return twemoji.parse(escaped);
  }, [comment.text]);
  
  return (
    <div 
      className="comment-text"
      dangerouslySetInnerHTML={{ __html: htmlContent }}
    />
  );
}
```

## Notes

- Filename is misleading - contains emoji library, not 3D lighting
- Twemoji is maintained by Twitter (now X)
- CDN-hosted emoji images
- Supports both PNG and SVG formats
- Handles complex emoji sequences (skin tones, ZWJ)
