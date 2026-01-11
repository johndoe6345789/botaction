# viewer_stats.js

## Overview
Minified Sketchfab webpack chunk containing the Model Transfer popup component and related organization transfer functionality for moving models between accounts.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 9411
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Module "h0W9" - Transfer Model Popup
Complete UI for transferring/moving models between organizations:

### Configuration

**Transfer Help URL**:
```javascript
${hosts.faq}/s/article/Transferring-a-model-from-an-individual-account-into-an-organization-account
```

### Form Fields (Schema B)

| Field | Validators | Initial Value |
|-------|------------|---------------|
| `org` | required | User's org UID or empty |
| `orgProject` | required ("No project selected") | undefined |
| `visibility` | oneOf: public, private, protected, org | "org" |
| `password` | conditional (required if protected) | "" |

### Organization Select Component (H)
**Props**:
- `value` - Selected org UID
- `onChange` - Selection callback
- `disabled` - Disable state
- `filter` - Function to filter options

**Features**:
- Auto-selects first org if none selected
- Displays org avatar and name
- Paginated membership loading
- Contributor role filtering

### Role Check Function (L)
```javascript
(role) => isAtLeast(role, "contributor")
```
Filters organizations where user has at least contributor access.

### Main Transfer Component (Y)

**Props**:
- `popup` - Popup controller
- `model` - Model to transfer
- `form` - Form state
- `onTransferModelSuccess` - Success callback

**State**:
- `isLoading` - Transfer in progress
- `selectedOrg` - Currently selected organization

**Features**:
- Organization selection (for transfers from personal)
- Project/folder picker
- Visibility settings
- Password protection option
- Form validation
- Loading state UI
- Error messaging

### Transfer Process
1. Validate form fields
2. Set loading state
3. If moving within org: Update org project
4. If transferring: Call transfer API
5. Invalidate ES cache
6. Show success message
7. Close popup

### UI Components Used
- `Popup` - Modal container
- `OrgProjectPicker` - Project selection
- `VisibilitySettings` - Public/Private/Protected
- `Button` - Actions
- `Input` - Password field
- `Avatar` - Org avatars
- `Loader` - Loading state

### Messages
- **Loading**: "Model is being transferred/moved."
- **No Projects**: "There is no project available..."
- **Info**: "Transfer cannot be canceled."

## Dependencies
- React (components, hooks)
- Redux (state management)
- Form validation utilities
- API client

## Technical Details
- Higher-Order Component pattern (withForm)
- Async/await for API calls
- Redux cache invalidation
- Form state management

## Use Cases
1. Transfer model to organization
2. Move model between org projects
3. Change model visibility during transfer
4. Set password protection

## Notes
- Critical for organization workflows
- Cannot undo transfers (warning displayed)
- Requires contributor+ role
- Integrates with ES cache for consistency
