# viewer_inspector.js

## Overview
Minified Sketchfab webpack chunk containing a comprehensive form state management system with built-in validation support. Provides React hooks for form handling.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 7112
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Module "JVQt" - Form State Management
Core form handling system with React hooks:

**State Functions**:
- `O` - Check if form `hasChanged` or `isTouched`
- `b` - Get all form field values
- `v` - Run validators on form fields
- `p` - Update individual field state

**Main Form Hook (m)**:
- `initialState` - Starting form state
- `getProps` - Field prop generators
- `onSubmit` - Form submission handler
- `onReset` - Form reset handler
- `onFieldsChange` - Field change callback

**Form State Object**:
```javascript
{
  fields: {},        // Field values and metadata
  isSubmitting: false,  // Submission in progress
  hasSucceeded: false,  // Last submit succeeded
  errors: [],        // Form-level errors
  isTouched: false,  // Any field touched
  hasChanged: false  // Any field modified
}
```

### Module "1bEe" - Form Validators
Comprehensive validation library:

| Validator | Description |
|-----------|-------------|
| `Ei` | Minimum length |
| `BS` | Maximum length |
| `kE` | Exact length |
| `C1` | Required field |
| `Oi` | Regex pattern match |
| `Rx` | Number validation |
| `VV` | Minimum value |
| `Fp` | Maximum value |
| `kw` | One of (enum values) |
| `HQ` | URL validation |
| `Do` | Email validation |
| `Jh` | isEmail check |
| `Ml` | Conditional validator |
| `H5` | Field match (password confirm) |
| `wF` | Custom validator function |
| `dg` | File size limit |
| `FA` | Form button state helper |

### Module "xtQ3" - React HOC
Higher-Order Component for form wrapping:
- Wraps components with form context
- Provides form props to wrapped component
- Handles form lifecycle

## Dependencies
- React (hooks API)
- React Context API (form context)

## Technical Details
- Hook-based form management
- Declarative validation rules
- Async validation support
- Field-level and form-level validation
- Built-in common validators

## Use Cases
1. User registration forms
2. Model upload settings
3. Profile editing
4. Payment forms
5. Any form requiring validation

## Notes
- Comprehensive form solution
- Extensible validator system
- Performance optimized (minimal re-renders)
- Supports complex validation scenarios
