# model_page.js

## Overview

This file contains the **3D model viewer page and related features** - the main model viewing experience on Sketchfab. It includes the model display, reviews, downloads, sharing, and content protection.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~145KB (minified)
- **Type**: React page components
- **Framework**: React

## Core Components

### 1. ModelPage

Main model viewing page:

```javascript
<ModelPage
  model={model}
  user={currentUser}
  embedded={false}
  theatreMode={false}
/>

// Sections:
// - 3D Viewer (iframe embed)
// - Model info (name, author, description)
// - Actions (like, download, share, embed)
// - Comments
// - Related models
```

### 2. ReviewEditForm

Model review submission:

```javascript
<ReviewEditForm
  model={model}
  onSubmit={handleSubmit}
  initialRating={0}
/>

// Features:
// - Star rating (1-5)
// - Text review
// - Editing existing review
// - Validation
```

### 3. PasswordProtectedModel

Access control for protected models:

```javascript
<PasswordProtectedModel
  model={model}
  onUnlock={(password) => verifyPassword(password)}
>
  <ModelViewer model={model} />
</PasswordProtectedModel>

// Shows password input form
// Stores unlock in session
```

### 4. DeletedModel

Placeholder for removed content:

```javascript
<DeletedModel
  reason={deletionReason}
  showAppeal={true}
/>

// Reasons:
// - 'user_deleted': User removed
// - 'policy_violation': Content policy
// - 'dmca': Copyright takedown
// - 'account_deleted': Account removed
```

### 5. ModelVersions

Version comparison view:

```javascript
<ModelVersions
  model={model}
  versions={model.versions}
  onSelectVersion={(version) => loadVersion(version)}
/>

// Features:
// - Version history list
// - Side-by-side comparison
// - Restore previous version
```

## Model Actions

### Download Popup

```javascript
<DownloadPopup
  model={model}
  formats={['glb', 'gltf', 'fbx', 'obj', 'usdz']}
  onDownload={(format) => downloadModel(format)}
/>
```

### Embed Popup

```javascript
<EmbedPopup
  model={model}
  options={{
    autostart: true,
    ui_controls: true,
    ui_infos: false
  }}
  onCopy={() => copyToClipboard()}
/>

// Generates embed code:
// <iframe src="https://sketchfab.com/models/{id}/embed" ...></iframe>
```

### Share Popup

```javascript
<SharePopup
  model={model}
  shareUrl={model.viewerUrl}
  platforms={['twitter', 'facebook', 'pinterest', 'email']}
/>
```

## Content Protection

### Restricted Content Overlay

```javascript
<RestrictedContentOverlay
  model={model}
  userAllowsRestricted={user?.allowsRestricted}
  onConfirm={() => confirmAgeVerification()}
>
  {/* Model viewer hidden until confirmed */}
</RestrictedContentOverlay>
```

### AI-Generated Detection

```javascript
<AIGeneratedBadge
  isAIGenerated={model.isAIGenerated}
  aiProvider={model.aiProvider}
/>

// Shows badge for AI-created content
// Displays provider (Meshy, Tripo, etc.)
```

## Theatre Mode

Full-screen immersive view:

```javascript
<TheatreMode
  model={model}
  isActive={theatreMode}
  onExit={() => setTheatreMode(false)}
>
  <ModelViewer model={model} fullscreen />
</TheatreMode>

// Features:
// - Dark overlay
// - Hidden UI elements
// - Escape to exit
// - Click outside to close
```

## Model Stats

```javascript
<ModelStats model={model} />

// Displays:
// - Views: 10.5K
// - Likes: 523
// - Comments: 45
// - Downloads: 1.2K (if downloadable)
```

## Review System

### Display Reviews

```javascript
<ReviewList
  reviews={reviews}
  sortBy="recent"  // 'recent' | 'helpful' | 'rating'
  onLoadMore={loadMoreReviews}
  onUpvote={handleUpvote}
/>
```

### Rating Breakdown

```javascript
<RatingBreakdown
  averageRating={4.5}
  totalReviews={128}
  distribution={{
    5: 80,
    4: 30,
    3: 10,
    2: 5,
    1: 3
  }}
/>
```

## Model Properties

```javascript
const modelProperties = {
  // Basic info
  name: 'Model Name',
  description: 'Model description...',
  tags: ['car', 'vehicle', '3d'],
  
  // Technical
  vertexCount: 50000,
  faceCount: 25000,
  materialCount: 5,
  textureCount: 8,
  
  // Metadata
  createdAt: '2023-01-15',
  publishedAt: '2023-01-16',
  
  // Settings
  visibility: 'public',
  isDownloadable: true,
  license: { type: 'cc-by', name: 'CC Attribution' }
};
```

## Error States

### Processing Error Codes

```javascript
const errorCodes = {
  10: 'Upload failed - invalid file format',
  20: 'Processing failed - geometry error',
  30: 'Processing failed - texture error',
  40: 'Processing timeout',
  50: 'Unknown processing error'
};

<ModelError
  code={model.errorCode}
  message={errorCodes[model.errorCode]}
  onRetry={() => retryProcessing()}
/>
```

## Save/Publish Flow

```javascript
<ModelPublishFlow
  model={model}
  step={currentStep}  // 'settings' | 'visibility' | 'review'
  onSave={handleSave}
  onPublish={handlePublish}
>
  {/* Step content */}
</ModelPublishFlow>
```

## Usage Example

```jsx
function ModelViewPage({ modelId }) {
  const { model, loading, error } = useModel(modelId);
  const user = useCurrentUser();
  
  if (loading) return <ModelPageSkeleton />;
  if (error) return <ModelError error={error} />;
  
  if (model.isDeleted) {
    return <DeletedModel reason={model.deletionReason} />;
  }
  
  if (model.isPasswordProtected && !isUnlocked(modelId)) {
    return (
      <PasswordProtectedModel 
        model={model} 
        onUnlock={verifyAndStore}
      />
    );
  }
  
  return (
    <ModelPage
      model={model}
      user={user}
      onLike={handleLike}
      onDownload={handleDownload}
      onShare={handleShare}
    />
  );
}
```

## Notes

- Primary model viewing experience
- Integrates with iframe viewer API
- Handles various access control scenarios
- Full review and rating system
- Download in multiple formats
