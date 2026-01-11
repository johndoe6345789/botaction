# viewer_network.js

## Overview

This file contains **markdown editor toolbar components** - UI components for a rich text/markdown editor including formatting buttons, link insertion, and image upload. NOT network/API functionality as the filename suggests.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~42KB (minified)
- **Type**: React editor components
- **Framework**: React

## Core Components

### 1. MarkdownToolbar

Editor formatting toolbar:

```javascript
<MarkdownToolbar
  editor={editorRef}
  onInsert={handleInsert}
  features={['bold', 'italic', 'link', 'image', 'code', 'list']}
/>
```

### Toolbar Buttons

```javascript
const toolbarButtons = [
  // Text formatting
  { id: 'bold', icon: 'bold', label: 'Bold', shortcut: 'Ctrl+B', syntax: '**' },
  { id: 'italic', icon: 'italic', label: 'Italic', shortcut: 'Ctrl+I', syntax: '*' },
  { id: 'strikethrough', icon: 'strikethrough', label: 'Strikethrough', syntax: '~~' },
  
  // Headers
  { id: 'h1', icon: 'heading-1', label: 'Heading 1', syntax: '# ' },
  { id: 'h2', icon: 'heading-2', label: 'Heading 2', syntax: '## ' },
  { id: 'h3', icon: 'heading-3', label: 'Heading 3', syntax: '### ' },
  
  // Lists
  { id: 'ul', icon: 'list-ul', label: 'Bullet List', syntax: '- ' },
  { id: 'ol', icon: 'list-ol', label: 'Numbered List', syntax: '1. ' },
  { id: 'checklist', icon: 'check-square', label: 'Checklist', syntax: '- [ ] ' },
  
  // Code
  { id: 'code', icon: 'code', label: 'Inline Code', syntax: '`' },
  { id: 'codeblock', icon: 'code-block', label: 'Code Block', syntax: '```\n' },
  
  // Links and media
  { id: 'link', icon: 'link', label: 'Insert Link', shortcut: 'Ctrl+K' },
  { id: 'image', icon: 'image', label: 'Insert Image' },
  
  // Other
  { id: 'quote', icon: 'quote', label: 'Quote', syntax: '> ' },
  { id: 'hr', icon: 'minus', label: 'Horizontal Rule', syntax: '\n---\n' }
];
```

### 2. FormatButton

Individual toolbar button:

```javascript
<FormatButton
  icon={<BoldIcon />}
  label="Bold"
  shortcut="Ctrl+B"
  active={isBoldActive}
  onClick={() => toggleFormat('bold')}
/>
```

### 3. LinkPopup

Link insertion dialog:

```javascript
<LinkPopup
  isOpen={isLinkPopupOpen}
  onClose={() => setLinkPopupOpen(false)}
  onInsert={({ url, text }) => insertLink(url, text)}
  selectedText={selectedText}
/>
```

### Link Popup UI

```jsx
function LinkPopup({ isOpen, onClose, onInsert, selectedText }) {
  const [url, setUrl] = useState('');
  const [text, setText] = useState(selectedText || '');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onInsert({ url, text });
    onClose();
  };
  
  return (
    <Popup isOpen={isOpen} onClose={onClose}>
      <form onSubmit={handleSubmit}>
        <div className="form-field">
          <label htmlFor="link-text">Text</label>
          <input
            id="link-text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Link text"
          />
        </div>
        
        <div className="form-field">
          <label htmlFor="link-url">URL</label>
          <input
            id="link-url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            type="url"
            required
          />
        </div>
        
        <div className="popup-actions">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="primary">
            Insert Link
          </Button>
        </div>
      </form>
    </Popup>
  );
}
```

### 4. ImageUpload

Image insertion:

```javascript
<ImageUpload
  onUpload={handleImageUpload}
  onInsertUrl={handleInsertImageUrl}
  maxSize={5 * 1024 * 1024}  // 5MB
  accept={['image/jpeg', 'image/png', 'image/gif', 'image/webp']}
/>
```

### Image Upload Flow

```jsx
function ImageUpload({ onUpload, onInsertUrl }) {
  const [mode, setMode] = useState('upload');  // 'upload' | 'url'
  const [uploading, setUploading] = useState(false);
  
  const handleFileSelect = async (file) => {
    setUploading(true);
    try {
      const url = await uploadImage(file);
      onUpload(url);
    } catch (error) {
      showError(error.message);
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <div className="image-upload">
      <div className="image-upload__tabs">
        <button 
          className={mode === 'upload' ? 'active' : ''}
          onClick={() => setMode('upload')}
        >
          Upload
        </button>
        <button 
          className={mode === 'url' ? 'active' : ''}
          onClick={() => setMode('url')}
        >
          URL
        </button>
      </div>
      
      {mode === 'upload' ? (
        <FileDropzone
          onDrop={handleFileSelect}
          loading={uploading}
          accept="image/*"
        />
      ) : (
        <ImageUrlInput onSubmit={onInsertUrl} />
      )}
    </div>
  );
}
```

## Markdown Insertion

```javascript
// Insert markdown syntax
function insertMarkdown(editor, syntax, options = {}) {
  const { selectionStart, selectionEnd, value } = editor;
  const selectedText = value.substring(selectionStart, selectionEnd);
  
  let newText;
  let cursorOffset;
  
  if (options.wrap) {
    // Wrap selected text: **selected** 
    newText = syntax + selectedText + syntax;
    cursorOffset = syntax.length;
  } else if (options.prefix) {
    // Prefix line: ## selected
    newText = syntax + selectedText;
    cursorOffset = syntax.length;
  } else if (options.block) {
    // Block syntax: ```\nselected\n```
    newText = syntax + selectedText + (options.suffix || syntax);
    cursorOffset = syntax.length;
  }
  
  // Update editor value
  const before = value.substring(0, selectionStart);
  const after = value.substring(selectionEnd);
  editor.value = before + newText + after;
  
  // Update cursor position
  editor.selectionStart = selectionStart + cursorOffset;
  editor.selectionEnd = selectionStart + cursorOffset + selectedText.length;
  editor.focus();
}

// Usage
insertMarkdown(editor, '**', { wrap: true });  // Bold
insertMarkdown(editor, '## ', { prefix: true });  // H2
insertMarkdown(editor, '```\n', { block: true, suffix: '\n```' });  // Code block
```

## Keyboard Shortcuts

```javascript
const keyboardShortcuts = {
  'ctrl+b': 'bold',
  'ctrl+i': 'italic',
  'ctrl+k': 'link',
  'ctrl+shift+c': 'code',
  'ctrl+shift+k': 'codeblock',
  'ctrl+shift+l': 'ul',
  'ctrl+shift+o': 'ol'
};

function handleKeyDown(e, editor) {
  const key = [
    e.ctrlKey && 'ctrl',
    e.shiftKey && 'shift',
    e.key.toLowerCase()
  ].filter(Boolean).join('+');
  
  const action = keyboardShortcuts[key];
  if (action) {
    e.preventDefault();
    executeAction(action, editor);
  }
}
```

## Usage Example

```jsx
function DescriptionEditor({ value, onChange }) {
  const editorRef = useRef(null);
  
  const handleToolbarAction = (action, data) => {
    const editor = editorRef.current;
    
    switch (action) {
      case 'bold':
        insertMarkdown(editor, '**', { wrap: true });
        break;
      case 'link':
        insertMarkdown(editor, `[${data.text}](${data.url})`);
        break;
      case 'image':
        insertMarkdown(editor, `![${data.alt}](${data.url})`);
        break;
      // ... more actions
    }
    
    onChange(editor.value);
  };
  
  return (
    <div className="markdown-editor">
      <MarkdownToolbar
        editor={editorRef}
        onAction={handleToolbarAction}
      />
      
      <textarea
        ref={editorRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Write your description..."
      />
      
      <MarkdownPreview content={value} />
    </div>
  );
}
```

## CSS Classes

```css
/* Toolbar */
.markdown-toolbar { }
.markdown-toolbar__group { }
.markdown-toolbar__button { }
.markdown-toolbar__button--active { }
.markdown-toolbar__divider { }

/* Popups */
.link-popup { }
.image-upload { }
.image-upload__tabs { }
.image-upload__dropzone { }

/* Editor */
.markdown-editor { }
.markdown-editor__textarea { }
.markdown-preview { }
```

## Notes

- Filename is misleading - contains editor toolbar, not network functionality
- Full markdown formatting toolbar
- Link and image insertion dialogs
- Keyboard shortcuts support
- File upload for images
- Preview capability
