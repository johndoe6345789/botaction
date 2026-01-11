# viewer_loading.js

## Overview
Minified Sketchfab webpack chunk containing organization and project management utilities, including role management, project pickers, and search functionality.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 7386
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Module "pgZm" - Organization Utilities
Core organization and project management:

**Role Hierarchy**:
```javascript
["spectator", "contributor", "project_lead", "admin"]
```

**Functions**:
| Function | Description |
|----------|-------------|
| `r` | Role comparison (hierarchy check) |
| `s` | `isContributor` check |
| `n` | Project route builder |
| `c` | Check if root project (depth === 0) |

### Module "gmGo" - Search Input Component
Reusable search input with styling:

**Props**:
- `className` - Additional CSS classes
- `placeholder` - Placeholder text
- `maxLength` - Character limit (default: 120)

**Features**:
- Font Awesome search icon (`fa-regular fa-search`)
- Auto-capitalization disabled
- Auto-complete disabled
- Auto-correct disabled
- Selenium test attribute included

### Module "2bV5" - Create Project Popup
**Hook**: `useCreateProjectPopup`
- Returns callback for opening project creation modal
- Lazy-loads popup component
- Handles `onProjectCreated` callback

### Module "V29b" - User Memberships
**Hook**: `useUserMemberships`
- Redux selector integration
- Pagination support
- API calls for membership data
- Auto-loads on user ID change

### Module "UzvP" - Organization Projects Search
**Hook**: `useOrgProjectsSearch`
- Paginated API search
- Cursor-based pagination
- Search query support
- Auto-loads on org/query change

### Module "FbSi" - User Org Role
**Hook**: `useUserOrgRole`
- Gets current user's role in organization
- Redux state integration
- API fallback for missing data

### Module "kN3w" - Project/Folder Picker
**Component**: `ProjectFolderPicker`

**Features**:
- Hierarchical folder navigation
- Project selection with thumbnails
- Breadcrumb-style navigation
- Empty state handling
- "Create new project" option
- Admin/staff permission checks
- Infinite scroll loading

**Props**:
- `orgUid` - Organization UID
- `onChange` - Selection callback
- `value` - Currently selected project
- `onNavigate` - Navigation callback
- `className` - CSS classes
- `disabled` - Disable picker

### Module "mwAa" - Paginated Project Select
**Component**: `PaginatedProjectSelect`
- Dropdown with paginated loading
- Bottom-reached detection for lazy loading
- Project thumbnails support

## Dependencies
- React (hooks, components)
- Redux (state management)
- Font Awesome (icons)
- Custom pagination utilities

## Technical Details
- Role-based access control
- Cursor-based pagination for performance
- Lazy loading of project lists
- Redux integration for state

## Use Cases
1. Organization management interfaces
2. Project selection in model transfers
3. Team membership management
4. Project/folder browsing
5. Role-based permission checking

## Notes
- Critical for Sketchfab's organization features
- Supports nested project hierarchies
- Performance optimized for large organizations
- Accessible keyboard navigation
