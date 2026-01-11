# viewer_animation.js

## Overview

This file contains **React UI components for forms, links, and organization features** - NOT animation code despite its filename. It includes model display components, organization utilities, and form elements.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~92KB (minified)
- **Type**: React UI components
- **Framework**: React

## Core Components

### 1. Fab.com URL Utilities (`XUjw`)

```javascript
const FabUrls = {
  baseUrl: 'https://www.fab.com',
  modelUrl: (modelId) => `${baseUrl}/listings/${modelId}`,
  searchUrl: (query) => `${baseUrl}/search?q=${encodeURIComponent(query)}`,
  userUrl: (username) => `${baseUrl}/sellers/${username}`
};
```

### 2. Help Tooltip (`rzLk`)

Contextual help tooltips:

```javascript
<HelpTooltip>
  This is helpful information about this feature.
</HelpTooltip>

// Props:
// - placement: 'top' | 'bottom' | 'left' | 'right'
// - children: Tooltip content
// - icon: Custom icon (default: question mark)
```

### 3. Message Component (`GKm7`)

Status messages and alerts:

```javascript
<Message type="success">Operation completed successfully!</Message>
<Message type="error">An error occurred. Please try again.</Message>
<Message type="warning">This action cannot be undone.</Message>
<Message type="info">Models are processed automatically.</Message>
```

### 4. ModelName Component (`ZZB/`)

Model name with visibility indicator:

```javascript
<ModelName
  model={model}
  showVisibility={true}
  linked={true}
  className="custom-class"
/>

// Displays:
// - Model name text
// - Visibility icon (private/protected/org-only)
// - Optional link to model page
```

### 5. ModelLink Component (`XxrW`)

Link to model page:

```javascript
<ModelLink model={model}>
  View Model
</ModelLink>

// Features:
// - Automatically constructs URL
// - Handles external links
// - Click tracking
```

### 6. Select Dropdown (`f49s`)

Form select component:

```javascript
<Select
  value={selected}
  onChange={setSelected}
  options={[
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2', disabled: true },
    { value: 'option3', label: 'Option 3' }
  ]}
  placeholder="Select an option..."
  searchable={true}
  clearable={true}
/>
```

### 7. ClientOnly Render (`l9Gv`)

Renders only on client-side:

```javascript
<ClientOnly fallback={<Skeleton />}>
  <ComponentThatNeedsBrowser />
</ClientOnly>

// Prevents SSR hydration mismatches
```

### 8. Lazy Image (`TC9H`)

Lazy-loaded images:

```javascript
<LazyImage
  src="/path/to/image.jpg"
  alt="Description"
  placeholder="/path/to/placeholder.jpg"
  threshold={200}  // Pixels before viewport to start loading
/>
```

### 9. Effect Hook Wrapper (`R276`)

```javascript
// useEffect that only runs on mount
useEffectOnce(() => {
  // Initialization code
});

// useEffect with cleanup handling
useEffectWithCleanup(
  () => {
    const subscription = subscribe();
    return () => subscription.unsubscribe();
  },
  [dependencies]
);
```

### 10. Organization Utilities (`4sJl`)

#### Role Permission Checking

```javascript
const OrgRoles = {
  SPECTATOR: 'spectator',
  CONTRIBUTOR: 'contributor',
  PROJECT_LEAD: 'project_lead',
  ADMIN: 'admin',
  OWNER: 'owner'
};

// Check if user can perform action
const canEdit = hasOrgPermission(user, org, 'contributor');
const canManage = hasOrgPermission(user, org, 'admin');
```

#### Breadcrumb Generation

```javascript
const breadcrumbs = getOrgBreadcrumbs(org, project);
// Returns:
// [
//   { label: 'Organization Name', href: '/orgs/org-slug' },
//   { label: 'Project Name', href: '/orgs/org-slug/projects/project-id' }
// ]
```

## Organization Role Hierarchy

```javascript
// Permissions by role:
const permissions = {
  spectator: ['view'],
  contributor: ['view', 'upload', 'comment'],
  project_lead: ['view', 'upload', 'comment', 'manage_project'],
  admin: ['view', 'upload', 'comment', 'manage_project', 'manage_members'],
  owner: ['view', 'upload', 'comment', 'manage_project', 'manage_members', 'manage_org']
};
```

## Usage Examples

### Model Card

```jsx
function ModelCard({ model }) {
  return (
    <div className="model-card">
      <LazyImage src={model.thumbnail} alt={model.name} />
      <ModelName model={model} showVisibility linked />
      <span className="author">{model.user.displayName}</span>
    </div>
  );
}
```

### Organization Project List

```jsx
function ProjectList({ org }) {
  const canCreate = hasOrgPermission(currentUser, org, 'contributor');
  
  return (
    <div>
      <Breadcrumbs items={getOrgBreadcrumbs(org)} />
      {canCreate && <Button>Create Project</Button>}
      {projects.map(project => (
        <ProjectItem key={project.uid} project={project} />
      ))}
    </div>
  );
}
```

### Form with Select

```jsx
function ModelSettings() {
  const [visibility, setVisibility] = useState('public');
  
  return (
    <form>
      <Select
        label="Visibility"
        value={visibility}
        onChange={setVisibility}
        options={[
          { value: 'public', label: 'Public' },
          { value: 'private', label: 'Private' },
          { value: 'protected', label: 'Password Protected' }
        ]}
      />
      <HelpTooltip>
        Choose who can view this model
      </HelpTooltip>
    </form>
  );
}
```

## CSS Classes

```css
.message { }
.message--success { }
.message--error { }
.message--warning { }
.message--info { }

.model-name { }
.model-name__text { }
.model-name__visibility { }

.select { }
.select__trigger { }
.select__options { }
.select__option { }
.select__option--selected { }
```

## Notes

- Filename is misleading - contains no animation code
- Part of Sketchfab's component library
- Integrates with organization permission system
- SSR-compatible with ClientOnly wrapper
