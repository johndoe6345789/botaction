# viewer_loading.js

## Overview

This file contains **organization project management components** - UI for managing organization workspaces, team projects, and collaborative features. NOT loading indicators as the filename suggests.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~55KB (minified)
- **Type**: React organization components
- **Framework**: React

## Core Components

### 1. OrganizationDashboard

Main org management view:

```javascript
<OrganizationDashboard
  organization={org}
  currentUser={user}
  activeTab="projects"
/>
```

### 2. ProjectList

Organization projects:

```javascript
<ProjectList
  projects={projects}
  onCreateProject={handleCreate}
  onEditProject={handleEdit}
  onDeleteProject={handleDelete}
  sortBy="updatedAt"
  view="grid"  // 'grid' | 'list'
/>
```

### Project Card

```jsx
function ProjectCard({ project }) {
  return (
    <div className="project-card">
      <div className="project-card__thumbnail">
        {project.thumbnail ? (
          <img src={project.thumbnail} alt={project.name} />
        ) : (
          <ProjectPlaceholder />
        )}
      </div>
      
      <div className="project-card__content">
        <h3 className="project-card__name">{project.name}</h3>
        <p className="project-card__description">{project.description}</p>
        
        <div className="project-card__meta">
          <span className="project-card__model-count">
            {project.modelCount} models
          </span>
          <span className="project-card__updated">
            Updated {formatRelativeTime(project.updatedAt)}
          </span>
        </div>
        
        <div className="project-card__members">
          <AvatarGroup users={project.members} max={3} />
        </div>
      </div>
    </div>
  );
}
```

### 3. CreateProjectModal

New project creation:

```javascript
<CreateProjectModal
  isOpen={isCreateOpen}
  onClose={() => setCreateOpen(false)}
  organization={org}
  onSuccess={handleProjectCreated}
/>
```

### Project Form

```jsx
function ProjectForm({ onSubmit, initialValues }) {
  const [values, setValues] = useState({
    name: '',
    description: '',
    visibility: 'team',
    ...initialValues
  });
  
  return (
    <form onSubmit={() => onSubmit(values)}>
      <FormField label="Project Name" required>
        <Input
          value={values.name}
          onChange={(e) => setValues({ ...values, name: e.target.value })}
          placeholder="My Project"
          maxLength={100}
        />
      </FormField>
      
      <FormField label="Description">
        <Textarea
          value={values.description}
          onChange={(e) => setValues({ ...values, description: e.target.value })}
          placeholder="Project description..."
          maxLength={500}
        />
      </FormField>
      
      <FormField label="Visibility">
        <RadioGroup
          value={values.visibility}
          onChange={(v) => setValues({ ...values, visibility: v })}
          options={[
            { value: 'team', label: 'Team Only', description: 'Only org members can access' },
            { value: 'public', label: 'Public', description: 'Anyone can view' }
          ]}
        />
      </FormField>
      
      <Button type="submit">Create Project</Button>
    </form>
  );
}
```

### 4. TeamMembers

Organization member management:

```javascript
<TeamMembers
  organization={org}
  members={members}
  pendingInvites={invites}
  currentUser={user}
  onInvite={handleInvite}
  onRemove={handleRemove}
  onChangeRole={handleChangeRole}
/>
```

### Member Roles

```javascript
const memberRoles = {
  owner: {
    name: 'Owner',
    permissions: ['all'],
    description: 'Full access to organization'
  },
  admin: {
    name: 'Admin',
    permissions: ['manage_members', 'manage_projects', 'manage_settings'],
    description: 'Can manage team and projects'
  },
  member: {
    name: 'Member',
    permissions: ['view', 'edit_models', 'create_projects'],
    description: 'Can create and edit content'
  },
  viewer: {
    name: 'Viewer',
    permissions: ['view'],
    description: 'Can only view content'
  }
};
```

### 5. InviteMemberModal

Team invitations:

```javascript
<InviteMemberModal
  isOpen={isInviteOpen}
  onClose={() => setInviteOpen(false)}
  organization={org}
  onInvite={handleInvite}
/>
```

### Invite Form

```jsx
function InviteForm({ onSubmit }) {
  const [emails, setEmails] = useState('');
  const [role, setRole] = useState('member');
  
  return (
    <form onSubmit={() => onSubmit({ emails: parseEmails(emails), role })}>
      <FormField label="Email Addresses" required>
        <Textarea
          value={emails}
          onChange={(e) => setEmails(e.target.value)}
          placeholder="Enter email addresses (one per line)"
        />
        <FormHelp>Separate multiple emails with commas or new lines</FormHelp>
      </FormField>
      
      <FormField label="Role">
        <Select
          value={role}
          onChange={setRole}
          options={[
            { value: 'admin', label: 'Admin' },
            { value: 'member', label: 'Member' },
            { value: 'viewer', label: 'Viewer' }
          ]}
        />
      </FormField>
      
      <Button type="submit">Send Invitations</Button>
    </form>
  );
}
```

### 6. ProjectSettings

Project configuration:

```javascript
<ProjectSettings
  project={project}
  onSave={handleSave}
  onDelete={handleDelete}
  canDelete={userCanDelete}
/>
```

### Settings Sections

```jsx
function ProjectSettings({ project, onSave }) {
  return (
    <div className="project-settings">
      <SettingsSection title="General">
        <ProjectForm 
          initialValues={project} 
          onSubmit={onSave} 
        />
      </SettingsSection>
      
      <SettingsSection title="Members">
        <ProjectMembers project={project} />
      </SettingsSection>
      
      <SettingsSection title="Integrations">
        <ProjectIntegrations project={project} />
      </SettingsSection>
      
      <SettingsSection title="Danger Zone" danger>
        <DeleteProjectButton project={project} />
      </SettingsSection>
    </div>
  );
}
```

## Organization Object

```javascript
const organization = {
  uid: 'org-123',
  name: 'Acme Corp',
  slug: 'acme-corp',
  
  // Branding
  logo: 'https://...',
  description: 'Company description',
  website: 'https://acme.com',
  
  // Settings
  visibility: 'private',
  allowPublicProjects: true,
  defaultMemberRole: 'member',
  
  // Counts
  memberCount: 25,
  projectCount: 12,
  modelCount: 450,
  
  // Subscription
  plan: 'business',
  maxMembers: 50,
  maxProjects: 100
};
```

## Project Object

```javascript
const project = {
  uid: 'proj-123',
  name: 'Q4 Marketing Assets',
  description: 'Product renders for Q4 campaign',
  
  // Organization
  organization: { uid: 'org-123', name: 'Acme Corp' },
  
  // Content
  modelCount: 45,
  models: [...],
  
  // Team
  members: [
    { user: {...}, role: 'admin' },
    { user: {...}, role: 'member' }
  ],
  
  // Settings
  visibility: 'team',
  
  // Timestamps
  createdAt: '2024-01-15T00:00:00Z',
  updatedAt: '2024-03-20T00:00:00Z'
};
```

## Usage Examples

### Organization Page

```jsx
function OrganizationPage({ orgSlug }) {
  const { organization, loading } = useOrganization(orgSlug);
  const [tab, setTab] = useState('projects');
  
  if (loading) return <OrganizationSkeleton />;
  
  return (
    <div className="org-page">
      <OrganizationHeader org={organization} />
      
      <Tabs value={tab} onChange={setTab}>
        <Tab value="projects" label="Projects" />
        <Tab value="members" label="Members" />
        <Tab value="settings" label="Settings" />
      </Tabs>
      
      {tab === 'projects' && (
        <ProjectList 
          organizationId={organization.uid}
          onCreateProject={() => setCreateOpen(true)}
        />
      )}
      
      {tab === 'members' && (
        <TeamMembers organization={organization} />
      )}
      
      {tab === 'settings' && (
        <OrganizationSettings organization={organization} />
      )}
    </div>
  );
}
```

## CSS Classes

```css
/* Projects */
.project-list { }
.project-card { }
.project-card__thumbnail { }
.project-card__content { }
.project-card__name { }
.project-card__meta { }
.project-card__members { }

/* Team */
.team-members { }
.member-row { }
.member-row__avatar { }
.member-row__info { }
.member-row__role { }
.member-row__actions { }

/* Settings */
.project-settings { }
.settings-section { }
.settings-section--danger { }
```

## Notes

- Filename is misleading - contains org/project management, not loading states
- Full organization workspace management
- Team member and role management
- Project creation and settings
- Collaborative features for teams
