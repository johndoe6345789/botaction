# viewer_audio.js

## Overview

This file contains **comment system and interaction components** - NOT audio handling. It provides comment editing, emoji support, popup systems, and model information display.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~82KB (minified)
- **Type**: Comment and interaction UI
- **Framework**: React

## Core Components

### 1. Scroll Prevention (`uo4Z`)

Prevents body scroll when modals are open:

```javascript
// Disable body scroll
disableBodyScroll(modalElement);

// Re-enable body scroll
enableBodyScroll(modalElement);

// Clear all scroll locks
clearAllBodyScrollLocks();

// Usage
function Modal({ isOpen, children }) {
  const ref = useRef();
  
  useEffect(() => {
    if (isOpen) {
      disableBodyScroll(ref.current);
      return () => enableBodyScroll(ref.current);
    }
  }, [isOpen]);
  
  return <div ref={ref}>{children}</div>;
}
```

### 2. Natural Sort (`l5lH`)

Human-friendly sorting:

```javascript
const items = ['item2', 'item10', 'item1'];

// Standard sort (wrong order)
items.sort();  // ['item1', 'item10', 'item2']

// Natural sort (correct order)
items.sort(naturalSort);  // ['item1', 'item2', 'item10']

// With locale
naturalSort('ä', 'z', { locale: 'de' });  // Correct German sorting
```

### 3. Comment Editor (`bWE4`)

Rich text comment editor:

```javascript
<CommentEditor
  value={comment}
  onChange={setComment}
  placeholder="Write a comment..."
  maxLength={2000}
  onSubmit={handleSubmit}
  onCancel={handleCancel}
  mentions={users}           // @mention support
  emojis={true}             // Emoji picker
  formatting={['bold', 'italic', 'link']}
/>
```

### Features

```javascript
// Mention autocomplete
// Type @ to trigger user autocomplete
// @username → linked mention

// Emoji support
// Type : to trigger emoji autocomplete
// :smile: → 😊

// Basic formatting
// **bold** → bold
// *italic* → italic
// [link](url) → link
```

### 4. Emoji Picker (`zoil`)

Emoji selection interface:

```javascript
<EmojiPicker
  onSelect={(emoji) => insertEmoji(emoji)}
  recent={recentEmojis}
  categories={['people', 'nature', 'food', 'activity', 'travel', 'objects']}
/>
```

### 5. Popup System (`isBB/qlM8`)

Modal and popup components:

```javascript
// Basic popup
<Popup
  isOpen={isOpen}
  onClose={handleClose}
  title="Popup Title"
  footer={
    <>
      <Button onClick={handleCancel}>Cancel</Button>
      <Button onClick={handleConfirm} primary>Confirm</Button>
    </>
  }
>
  <p>Popup content here</p>
</Popup>

// Confirmation dialog
const confirmed = await confirm({
  title: 'Delete Comment',
  message: 'Are you sure you want to delete this comment?',
  confirmLabel: 'Delete',
  cancelLabel: 'Cancel',
  destructive: true
});
```

### 6. Model Information Display

Model metadata component:

```javascript
<ModelInfo
  model={model}
  showStats={true}
  showAuthor={true}
  showTags={true}
/>

// Displays:
// - Model name
// - Author with avatar
// - View/like/download counts
// - Tags
// - License info
// - Creation date
```

### 7. Comment Thread

Threaded comment display:

```javascript
<CommentThread
  comments={comments}
  modelId={modelId}
  currentUser={user}
  onReply={handleReply}
  onEdit={handleEdit}
  onDelete={handleDelete}
  onLike={handleLike}
/>
```

### Comment Structure

```javascript
const comment = {
  uid: 'comment-123',
  body: 'Great model!',
  user: {
    uid: 'user-456',
    displayName: 'John Doe',
    avatar: 'https://...'
  },
  createdAt: '2023-01-15T10:30:00Z',
  updatedAt: null,
  likeCount: 5,
  isLiked: false,
  replies: [
    // Nested comments
  ]
};
```

## Popup Types

### Modal

```javascript
<Modal
  isOpen={isOpen}
  onClose={handleClose}
  size="medium"  // 'small' | 'medium' | 'large' | 'fullscreen'
  closeOnOverlayClick={true}
  closeOnEscape={true}
>
  {content}
</Modal>
```

### Tooltip

```javascript
<Tooltip content="This is a tooltip" placement="top">
  <Button>Hover me</Button>
</Tooltip>
```

### Dropdown

```javascript
<Dropdown
  trigger={<Button>Click me</Button>}
  isOpen={isOpen}
  onClose={handleClose}
>
  <DropdownItem onClick={handleOption1}>Option 1</DropdownItem>
  <DropdownItem onClick={handleOption2}>Option 2</DropdownItem>
</Dropdown>
```

## Comment Actions

### Like/Unlike

```javascript
const handleLike = async (commentId) => {
  if (comment.isLiked) {
    await api.unlikeComment(commentId);
  } else {
    await api.likeComment(commentId);
  }
};
```

### Reply

```javascript
const handleReply = (parentId) => {
  setReplyingTo(parentId);
  focusCommentEditor();
};
```

### Delete

```javascript
const handleDelete = async (commentId) => {
  const confirmed = await confirm({
    title: 'Delete Comment',
    message: 'Are you sure?',
    destructive: true
  });
  
  if (confirmed) {
    await api.deleteComment(commentId);
    removeComment(commentId);
  }
};
```

## Usage Examples

### Comment Section

```jsx
function CommentSection({ modelId }) {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const user = useCurrentUser();
  
  const handleSubmit = async () => {
    const comment = await api.createComment(modelId, newComment);
    setComments([comment, ...comments]);
    setNewComment('');
  };
  
  return (
    <div className="comment-section">
      {user && (
        <CommentEditor
          value={newComment}
          onChange={setNewComment}
          onSubmit={handleSubmit}
        />
      )}
      <CommentThread
        comments={comments}
        modelId={modelId}
        currentUser={user}
      />
    </div>
  );
}
```

## CSS Classes

```css
.comment-editor { }
.comment-editor__textarea { }
.comment-editor__toolbar { }
.comment-editor__emoji-picker { }

.comment-thread { }
.comment-thread__item { }
.comment-thread__replies { }

.popup { }
.popup__overlay { }
.popup__content { }
.popup__header { }
.popup__body { }
.popup__footer { }
```

## Notes

- Filename is misleading - contains comment system, not audio
- Full comment CRUD functionality
- Emoji and mention support
- Accessible popup system with focus management
- Integrates with Sketchfab's API
