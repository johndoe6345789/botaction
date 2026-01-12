# viewer_analytics.js

## Overview

This file contains **dropdown and select components** - React UI components for dropdown menus, select inputs, and comboboxes. NOT analytics tracking as the filename suggests.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~48KB (minified)
- **Type**: React form components
- **Framework**: React

## Core Components

### 1. Select

Basic select dropdown:

```javascript
<Select
  value={selectedValue}
  onChange={setSelectedValue}
  options={[
    { value: 'opt1', label: 'Option 1' },
    { value: 'opt2', label: 'Option 2' },
    { value: 'opt3', label: 'Option 3', disabled: true }
  ]}
  placeholder="Select an option"
/>
```

### Select Props

```javascript
Select.propTypes = {
  // Value
  value: PropTypes.any,
  onChange: PropTypes.func.isRequired,
  
  // Options
  options: PropTypes.arrayOf(PropTypes.shape({
    value: PropTypes.any.isRequired,
    label: PropTypes.string.isRequired,
    disabled: PropTypes.bool,
    icon: PropTypes.node
  })).isRequired,
  
  // Appearance
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  variant: PropTypes.oneOf(['default', 'outlined', 'filled']),
  fullWidth: PropTypes.bool,
  
  // State
  disabled: PropTypes.bool,
  error: PropTypes.bool,
  required: PropTypes.bool,
  
  // Content
  placeholder: PropTypes.string,
  label: PropTypes.string,
  helperText: PropTypes.string,
  errorText: PropTypes.string
};
```

### 2. MultiSelect

Multiple selection dropdown:

```javascript
<MultiSelect
  value={selectedValues}
  onChange={setSelectedValues}
  options={categories}
  placeholder="Select categories"
  maxSelections={3}
  showTags={true}
/>
```

### MultiSelect Features

```javascript
// With tags
<MultiSelect
  value={['cat1', 'cat2']}
  showTags={true}
  tagVariant="chip"  // 'chip' | 'badge'
  onRemoveTag={(value) => removeValue(value)}
/>

// With select all
<MultiSelect
  options={options}
  showSelectAll={true}
  selectAllLabel="Select All"
/>

// With search
<MultiSelect
  options={options}
  searchable={true}
  searchPlaceholder="Search options..."
/>
```

### 3. Dropdown

Generic dropdown container:

```javascript
<Dropdown
  trigger={<button>Open Menu</button>}
  placement="bottom-start"
  offset={[0, 8]}
>
  <DropdownMenu>
    <DropdownItem onClick={action1}>Action 1</DropdownItem>
    <DropdownItem onClick={action2}>Action 2</DropdownItem>
    <DropdownDivider />
    <DropdownItem onClick={action3} danger>Delete</DropdownItem>
  </DropdownMenu>
</Dropdown>
```

### Dropdown Placements

```javascript
const placements = [
  'top',
  'top-start',
  'top-end',
  'bottom',
  'bottom-start',
  'bottom-end',
  'left',
  'left-start',
  'left-end',
  'right',
  'right-start',
  'right-end'
];
```

### 4. Combobox

Searchable dropdown with autocomplete:

```javascript
<Combobox
  value={selectedUser}
  onChange={setSelectedUser}
  options={users}
  getOptionLabel={(user) => user.name}
  getOptionValue={(user) => user.id}
  placeholder="Search users..."
  noOptionsText="No users found"
/>
```

### Async Combobox

```javascript
<Combobox
  value={selected}
  onChange={setSelected}
  loadOptions={async (query) => {
    const response = await fetch(`/api/search?q=${query}`);
    return response.json();
  }}
  debounce={300}
  minQueryLength={2}
  loadingText="Searching..."
/>
```

### 5. DropdownMenu

Menu items container:

```javascript
<DropdownMenu>
  <DropdownLabel>User Actions</DropdownLabel>
  
  <DropdownItem icon={<EditIcon />} onClick={editProfile}>
    Edit Profile
  </DropdownItem>
  
  <DropdownItem icon={<SettingsIcon />} onClick={openSettings}>
    Settings
  </DropdownItem>
  
  <DropdownDivider />
  
  <DropdownItem icon={<LogoutIcon />} onClick={logout} danger>
    Logout
  </DropdownItem>
</DropdownMenu>
```

### 6. NestedDropdown

Submenu support:

```javascript
<Dropdown trigger={<button>Menu</button>}>
  <DropdownMenu>
    <DropdownItem>Simple Item</DropdownItem>
    
    <NestedDropdown label="More Options">
      <DropdownItem>Nested Item 1</DropdownItem>
      <DropdownItem>Nested Item 2</DropdownItem>
      
      <NestedDropdown label="Even More">
        <DropdownItem>Deep Nested 1</DropdownItem>
        <DropdownItem>Deep Nested 2</DropdownItem>
      </NestedDropdown>
    </NestedDropdown>
  </DropdownMenu>
</Dropdown>
```

## Keyboard Navigation

```javascript
// Built-in keyboard support
const keyboardHandlers = {
  ArrowDown: 'Move to next option',
  ArrowUp: 'Move to previous option',
  Enter: 'Select focused option',
  Escape: 'Close dropdown',
  Home: 'Move to first option',
  End: 'Move to last option',
  'Type characters': 'Jump to matching option'
};
```

## Grouped Options

```javascript
<Select
  value={selected}
  onChange={setSelected}
  options={[
    {
      label: 'Fruits',
      options: [
        { value: 'apple', label: 'Apple' },
        { value: 'banana', label: 'Banana' }
      ]
    },
    {
      label: 'Vegetables',
      options: [
        { value: 'carrot', label: 'Carrot' },
        { value: 'broccoli', label: 'Broccoli' }
      ]
    }
  ]}
/>
```

## Custom Option Rendering

```javascript
<Select
  options={users}
  renderOption={(option, { selected, focused }) => (
    <div className={cn('option', { selected, focused })}>
      <Avatar src={option.avatar} size="small" />
      <span className="option-name">{option.name}</span>
      <span className="option-email">{option.email}</span>
    </div>
  )}
  renderValue={(selected) => (
    <div className="selected-value">
      <Avatar src={selected.avatar} size="small" />
      {selected.name}
    </div>
  )}
/>
```

## Usage Examples

### Category Filter

```jsx
function CategoryFilter({ onFilter }) {
  const [categories, setCategories] = useState([]);
  const categoryOptions = useCategoryOptions();
  
  const handleChange = (values) => {
    setCategories(values);
    onFilter({ categories: values });
  };
  
  return (
    <MultiSelect
      label="Categories"
      value={categories}
      onChange={handleChange}
      options={categoryOptions}
      placeholder="All categories"
      showTags
    />
  );
}
```

### User Selector

```jsx
function UserSelector({ value, onChange }) {
  const loadUsers = async (query) => {
    const response = await api.searchUsers(query);
    return response.users;
  };
  
  return (
    <Combobox
      value={value}
      onChange={onChange}
      loadOptions={loadUsers}
      getOptionLabel={(user) => user.displayName}
      getOptionValue={(user) => user.uid}
      renderOption={(user) => (
        <div className="user-option">
          <UserAvatar user={user} size="small" />
          <div>
            <div>{user.displayName}</div>
            <div className="username">@{user.username}</div>
          </div>
        </div>
      )}
      placeholder="Search users..."
    />
  );
}
```

### Sort Dropdown

```jsx
function SortDropdown({ value, onChange }) {
  return (
    <Dropdown
      trigger={
        <button className="sort-button">
          <SortIcon />
          Sort: {value.label}
        </button>
      }
    >
      <DropdownMenu>
        <DropdownItem 
          onClick={() => onChange({ value: 'recent', label: 'Most Recent' })}
          selected={value.value === 'recent'}
        >
          Most Recent
        </DropdownItem>
        <DropdownItem 
          onClick={() => onChange({ value: 'popular', label: 'Most Popular' })}
          selected={value.value === 'popular'}
        >
          Most Popular
        </DropdownItem>
        <DropdownItem 
          onClick={() => onChange({ value: 'likes', label: 'Most Liked' })}
          selected={value.value === 'likes'}
        >
          Most Liked
        </DropdownItem>
      </DropdownMenu>
    </Dropdown>
  );
}
```

## CSS Classes

```css
/* Select */
.select { }
.select--small { }
.select--medium { }
.select--large { }
.select--disabled { }
.select--error { }
.select__trigger { }
.select__placeholder { }
.select__value { }
.select__arrow { }

/* Dropdown */
.dropdown { }
.dropdown__trigger { }
.dropdown__content { }
.dropdown--open { }

/* Menu */
.dropdown-menu { }
.dropdown-item { }
.dropdown-item--focused { }
.dropdown-item--selected { }
.dropdown-item--disabled { }
.dropdown-item--danger { }
.dropdown-divider { }
.dropdown-label { }

/* MultiSelect */
.multi-select { }
.multi-select__tags { }
.multi-select__tag { }
.multi-select__tag-remove { }

/* Combobox */
.combobox { }
.combobox__input { }
.combobox__clear { }
.combobox__loading { }
```

## Notes

- Filename is misleading - contains dropdown components, not analytics
- Full keyboard navigation support
- Async option loading for combobox
- Nested dropdown menus
- Grouped options support
- Custom option/value rendering
