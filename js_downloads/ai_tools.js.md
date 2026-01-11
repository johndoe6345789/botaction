# ai_tools.js

## Overview

This file contains **Sketchfab's AI-powered creative tools configuration and UI components**. It defines the available AI actions for 3D content generation, provider integrations, and creative workflow interfaces.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~126KB (minified)
- **Type**: AI tools configuration and React components
- **Framework**: React

## AI Action Types

```javascript
const AI_ACTIONS = {
  IMAGE_GENERATION: 'image_generation',
  MESH_GENERATION_FROM_PROMPT: 'mesh_from_prompt',     // Text-to-3D
  MESH_GENERATION_FROM_IMAGE: 'mesh_from_image',       // Image-to-3D
  MESH_RIGGING: 'mesh_rigging',                        // Auto-rigging
  TEXTURE_GENERATION: 'texture_generation',            // AI texturing
  MESH_RETOPOLOGY: 'mesh_retopology'                   // Retopology
};
```

## AI Providers

Supported AI service providers with icons:

```javascript
const AI_PROVIDERS = {
  CSM: { name: 'CSM', icon: CsmIcon },
  FLUX: { name: 'FLUX', icon: FluxIcon },
  GEMINI: { name: 'Gemini', icon: GeminiIcon },
  MESHY: { name: 'Meshy', icon: MeshyIcon },
  RODIN: { name: 'Rodin', icon: RodinIcon },
  STABILITY: { name: 'Stability AI', icon: StabilityIcon },
  TRIPO: { name: 'Tripo', icon: TripoIcon }
};
```

## Core Components

### 1. CreativeWorkflow

Main AI workflow interface:

```javascript
<CreativeWorkflow
  action={AI_ACTIONS.MESH_GENERATION_FROM_PROMPT}
  onComplete={handleComplete}
  onError={handleError}
/>

// Features:
// - Step-by-step wizard interface
// - Progress tracking
// - Result preview
// - Export to Sketchfab
```

### 2. ProviderSelector

Choose AI provider:

```javascript
<ProviderSelector
  action={AI_ACTIONS.MESH_GENERATION_FROM_IMAGE}
  selected={selectedProvider}
  onSelect={handleProviderSelect}
/>

// Shows available providers for the selected action
// Displays provider capabilities and limitations
```

### 3. PromptInput

Text prompt for AI generation:

```javascript
<PromptInput
  value={prompt}
  onChange={setPrompt}
  maxLength={500}
  placeholder="Describe the 3D model you want to create..."
  suggestions={['a wooden chair', 'sci-fi spaceship', 'cartoon character']}
/>
```

### 4. ImageUploader

Image input for image-to-3D:

```javascript
<ImageUploader
  onUpload={handleImageUpload}
  accept="image/png,image/jpeg,image/webp"
  maxSize={10 * 1024 * 1024}  // 10MB
  preview={true}
/>

// Features:
// - Drag and drop
// - File type validation
// - Image preview
// - Background removal option
```

### 5. GenerationProgress

Progress display:

```javascript
<GenerationProgress
  status={status}  // 'queued' | 'processing' | 'complete' | 'failed'
  progress={0.65}  // 0-1
  eta={120}        // seconds remaining
  stage="Generating mesh..."
/>
```

### 6. ResultViewer

3D preview of generated model:

```javascript
<ResultViewer
  modelUrl={generatedModelUrl}
  onAccept={handleAccept}
  onRegenerate={handleRegenerate}
  onRefine={handleRefine}
/>

// Features:
// - Interactive 3D preview
// - Orbit controls
// - Multiple view angles
// - Accept/Regenerate actions
```

## AI Tool Configurations

### Text-to-3D

```javascript
const textTo3DConfig = {
  action: AI_ACTIONS.MESH_GENERATION_FROM_PROMPT,
  providers: ['MESHY', 'TRIPO', 'CSM'],
  inputs: {
    prompt: { type: 'text', required: true, maxLength: 500 },
    style: { type: 'select', options: ['realistic', 'stylized', 'low_poly'] },
    quality: { type: 'select', options: ['draft', 'standard', 'high'] }
  },
  outputs: {
    formats: ['glb', 'fbx', 'obj'],
    textures: true,
    rigging: false
  }
};
```

### Image-to-3D

```javascript
const imageTo3DConfig = {
  action: AI_ACTIONS.MESH_GENERATION_FROM_IMAGE,
  providers: ['TRIPO', 'RODIN', 'CSM', 'STABILITY'],
  inputs: {
    image: { type: 'image', required: true, formats: ['png', 'jpg', 'webp'] },
    removeBackground: { type: 'boolean', default: true },
    generateTexture: { type: 'boolean', default: true }
  },
  outputs: {
    formats: ['glb', 'fbx'],
    textures: true
  }
};
```

### Auto-Rigging

```javascript
const autoRiggingConfig = {
  action: AI_ACTIONS.MESH_RIGGING,
  providers: ['MESHY'],
  inputs: {
    model: { type: 'model', required: true, formats: ['glb', 'fbx'] },
    skeletonType: { type: 'select', options: ['humanoid', 'quadruped', 'custom'] }
  },
  outputs: {
    formats: ['glb', 'fbx'],
    animations: ['idle', 'walk', 'run']
  }
};
```

### Texture Generation

```javascript
const textureGenConfig = {
  action: AI_ACTIONS.TEXTURE_GENERATION,
  providers: ['STABILITY', 'FLUX'],
  inputs: {
    model: { type: 'model', required: true },
    prompt: { type: 'text', required: true },
    style: { type: 'select', options: ['photorealistic', 'painted', 'cartoon'] }
  },
  outputs: {
    textures: ['diffuse', 'normal', 'roughness', 'metallic']
  }
};
```

## API Integration

```javascript
// Start generation
const job = await api.ai.createJob({
  action: AI_ACTIONS.MESH_GENERATION_FROM_PROMPT,
  provider: 'MESHY',
  params: { prompt: 'a wooden chair', quality: 'standard' }
});

// Poll status
const status = await api.ai.getJobStatus(job.id);

// Get result
const result = await api.ai.getJobResult(job.id);

// Publish to Sketchfab
await api.ai.publishToSketchfab(job.id, {
  name: 'AI Generated Chair',
  description: 'Created with AI',
  tags: ['ai-generated', 'furniture']
});
```

## Feature Flags

```javascript
// User feature checks
if (user.features.includes('ai_text_to_3d')) {
  // Show text-to-3D option
}

if (user.features.includes('ai_image_to_mesh')) {
  // Show image-to-3D option
}

if (user.features.includes('ai_auto_rigging')) {
  // Show auto-rigging option
}
```

## Error Handling

```javascript
const AI_ERRORS = {
  QUOTA_EXCEEDED: 'You have reached your AI generation limit',
  INVALID_INPUT: 'Invalid input provided',
  GENERATION_FAILED: 'AI generation failed, please try again',
  PROVIDER_UNAVAILABLE: 'AI provider is temporarily unavailable',
  CONTENT_POLICY: 'Content violates usage policy'
};
```

## Credits System

```javascript
// Check remaining credits
const credits = user.aiCredits;

// Credit costs per action
const creditCosts = {
  [AI_ACTIONS.MESH_GENERATION_FROM_PROMPT]: 1,
  [AI_ACTIONS.MESH_GENERATION_FROM_IMAGE]: 2,
  [AI_ACTIONS.MESH_RIGGING]: 1,
  [AI_ACTIONS.TEXTURE_GENERATION]: 1
};
```
