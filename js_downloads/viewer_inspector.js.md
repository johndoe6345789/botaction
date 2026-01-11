# viewer_inspector.js

## Overview

This file contains **form validation utilities** - functions for validating user input in forms. NOT inspector/debugging tools as the filename suggests.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~32KB (minified)
- **Type**: Validation utilities
- **Framework**: Vanilla JavaScript

## Core Validation Functions

### Field Validators

```javascript
const validators = {
  // Required field
  required: (value) => {
    if (value === null || value === undefined || value === '') {
      return 'This field is required';
    }
    return null;
  },
  
  // Email format
  email: (value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (value && !emailRegex.test(value)) {
      return 'Please enter a valid email address';
    }
    return null;
  },
  
  // Minimum length
  minLength: (min) => (value) => {
    if (value && value.length < min) {
      return `Must be at least ${min} characters`;
    }
    return null;
  },
  
  // Maximum length
  maxLength: (max) => (value) => {
    if (value && value.length > max) {
      return `Must be no more than ${max} characters`;
    }
    return null;
  },
  
  // Pattern match
  pattern: (regex, message) => (value) => {
    if (value && !regex.test(value)) {
      return message || 'Invalid format';
    }
    return null;
  },
  
  // Number range
  range: (min, max) => (value) => {
    const num = Number(value);
    if (isNaN(num)) {
      return 'Must be a number';
    }
    if (num < min || num > max) {
      return `Must be between ${min} and ${max}`;
    }
    return null;
  },
  
  // URL format
  url: (value) => {
    try {
      if (value) new URL(value);
      return null;
    } catch {
      return 'Please enter a valid URL';
    }
  },
  
  // Match another field
  matches: (fieldName, fieldLabel) => (value, allValues) => {
    if (value !== allValues[fieldName]) {
      return `Must match ${fieldLabel}`;
    }
    return null;
  }
};
```

### Validation Runner

```javascript
// Validate a single field
function validateField(value, rules) {
  for (const rule of rules) {
    const error = rule(value);
    if (error) return error;
  }
  return null;
}

// Validate entire form
function validateForm(values, schema) {
  const errors = {};
  
  for (const [field, rules] of Object.entries(schema)) {
    const error = validateField(values[field], rules);
    if (error) {
      errors[field] = error;
    }
  }
  
  return errors;
}

// Check if form is valid
function isFormValid(errors) {
  return Object.keys(errors).length === 0;
}
```

### Usage Example

```javascript
// Define validation schema
const signupSchema = {
  username: [
    validators.required,
    validators.minLength(3),
    validators.maxLength(20),
    validators.pattern(/^[a-zA-Z0-9_]+$/, 'Only letters, numbers, and underscores')
  ],
  email: [
    validators.required,
    validators.email
  ],
  password: [
    validators.required,
    validators.minLength(8),
    validators.pattern(/[A-Z]/, 'Must contain uppercase letter'),
    validators.pattern(/[0-9]/, 'Must contain a number')
  ],
  confirmPassword: [
    validators.required,
    validators.matches('password', 'Password')
  ]
};

// Validate form
const values = {
  username: 'john_doe',
  email: 'john@example.com',
  password: 'SecurePass123',
  confirmPassword: 'SecurePass123'
};

const errors = validateForm(values, signupSchema);

if (isFormValid(errors)) {
  submitForm(values);
} else {
  displayErrors(errors);
}
```

## Async Validators

```javascript
// Async validation (e.g., check username availability)
const asyncValidators = {
  usernameAvailable: async (value) => {
    if (!value) return null;
    
    const response = await fetch(`/api/check-username?username=${value}`);
    const { available } = await response.json();
    
    if (!available) {
      return 'This username is already taken';
    }
    return null;
  },
  
  emailNotRegistered: async (value) => {
    if (!value) return null;
    
    const response = await fetch(`/api/check-email?email=${value}`);
    const { registered } = await response.json();
    
    if (registered) {
      return 'This email is already registered';
    }
    return null;
  }
};

// Validate with async
async function validateFieldAsync(value, rules, asyncRules = []) {
  // Run sync validators first
  const syncError = validateField(value, rules);
  if (syncError) return syncError;
  
  // Run async validators
  for (const asyncRule of asyncRules) {
    const error = await asyncRule(value);
    if (error) return error;
  }
  
  return null;
}
```

## Form Integration (React)

```javascript
// Custom hook for form validation
function useFormValidation(initialValues, schema) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  
  const handleChange = (field) => (e) => {
    const value = e.target.value;
    setValues(prev => ({ ...prev, [field]: value }));
    
    // Validate on change if field was touched
    if (touched[field]) {
      const error = validateField(value, schema[field] || []);
      setErrors(prev => ({ ...prev, [field]: error }));
    }
  };
  
  const handleBlur = (field) => () => {
    setTouched(prev => ({ ...prev, [field]: true }));
    
    const error = validateField(values[field], schema[field] || []);
    setErrors(prev => ({ ...prev, [field]: error }));
  };
  
  const validateAll = () => {
    const allErrors = validateForm(values, schema);
    setErrors(allErrors);
    setTouched(
      Object.keys(schema).reduce((acc, field) => ({ ...acc, [field]: true }), {})
    );
    return isFormValid(allErrors);
  };
  
  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    validateAll,
    isValid: isFormValid(errors)
  };
}
```

### Component Usage

```jsx
function SignupForm() {
  const {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    validateAll
  } = useFormValidation(
    { username: '', email: '', password: '' },
    signupSchema
  );
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateAll()) {
      // Submit form
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input
          name="username"
          value={values.username}
          onChange={handleChange('username')}
          onBlur={handleBlur('username')}
        />
        {touched.username && errors.username && (
          <span className="error">{errors.username}</span>
        )}
      </div>
      
      {/* More fields... */}
      
      <button type="submit">Sign Up</button>
    </form>
  );
}
```

## Specific Validators for Sketchfab

```javascript
// Model name validation
const modelNameValidators = [
  validators.required,
  validators.minLength(1),
  validators.maxLength(100),
  validators.pattern(/^[^<>]+$/, 'Cannot contain < or >')
];

// Tag validation
const tagValidator = (value) => {
  if (!Array.isArray(value)) return 'Invalid tags';
  if (value.length < 1) return 'Add at least one tag';
  if (value.length > 20) return 'Maximum 20 tags';
  if (value.some(tag => tag.length > 50)) return 'Tags must be under 50 characters';
  return null;
};

// Description validation
const descriptionValidators = [
  validators.maxLength(5000)
];

// Password strength
const passwordStrength = (value) => {
  if (!value) return null;
  
  let strength = 0;
  if (value.length >= 8) strength++;
  if (value.length >= 12) strength++;
  if (/[A-Z]/.test(value)) strength++;
  if (/[a-z]/.test(value)) strength++;
  if (/[0-9]/.test(value)) strength++;
  if (/[^A-Za-z0-9]/.test(value)) strength++;
  
  if (strength < 3) return 'Password is too weak';
  return null;
};
```

## Notes

- Filename is misleading - contains validation utilities, not inspector tools
- Synchronous and asynchronous validation support
- Composable validator functions
- React hook integration
- Sketchfab-specific validators for model/user forms
