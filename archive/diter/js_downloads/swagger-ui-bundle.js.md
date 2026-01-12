# swagger-ui-bundle.js

## Overview

This file contains **Swagger UI** - the interactive API documentation interface. It renders OpenAPI/Swagger specifications as an explorable, testable API documentation page.

## File Information

- **Status**: Active library
- **Size**: ~1.2MB (minified)
- **Version**: 4.x (based on code patterns)
- **Type**: API documentation UI

## Core Features

### Initialization

```javascript
const ui = SwaggerUIBundle({
  url: '/api/swagger.json',              // OpenAPI spec URL
  dom_id: '#swagger-ui',                 // Container element
  
  // Presets
  presets: [
    SwaggerUIBundle.presets.apis,
    SwaggerUIStandalonePreset
  ],
  
  // Plugins
  plugins: [
    SwaggerUIBundle.plugins.DownloadUrl
  ],
  
  // Layout
  layout: 'StandaloneLayout',
  
  // Behavior
  deepLinking: true,
  displayOperationId: false,
  displayRequestDuration: true,
  filter: true,
  showExtensions: true,
  showCommonExtensions: true,
  
  // Auth
  oauth2RedirectUrl: `${window.location.origin}/oauth2-redirect.html`,
  
  // Validation
  validatorUrl: null,
  
  // Network
  requestInterceptor: (request) => {
    request.headers['X-Custom-Header'] = 'value';
    return request;
  },
  responseInterceptor: (response) => {
    console.log('Response:', response);
    return response;
  }
});
```

### Configuration Options

```javascript
const swaggerConfig = {
  // Spec sources (use one)
  url: '/api/swagger.json',           // Load from URL
  spec: { /* inline OpenAPI spec */ }, // Inline spec object
  urls: [                              // Multiple specs
    { url: '/api/v1/swagger.json', name: 'V1' },
    { url: '/api/v2/swagger.json', name: 'V2' }
  ],
  
  // DOM
  dom_id: '#swagger-ui',
  domNode: document.getElementById('swagger-ui'),
  
  // Display
  docExpansion: 'list',       // 'none' | 'list' | 'full'
  defaultModelsExpandDepth: 1,
  defaultModelExpandDepth: 1,
  displayOperationId: false,
  displayRequestDuration: true,
  maxDisplayedTags: -1,
  filter: true,               // Enable filtering
  
  // Behavior
  deepLinking: true,          // URL hash updates
  persistAuthorization: true, // Save auth in localStorage
  tryItOutEnabled: true,      // Enable "Try it out"
  supportedSubmitMethods: ['get', 'put', 'post', 'delete', 'patch'],
  
  // Network
  withCredentials: false,
  requestSnippetsEnabled: true,
  requestSnippets: {
    generators: {
      curl_bash: { title: 'cURL (bash)', syntax: 'bash' },
      curl_cmd: { title: 'cURL (cmd)', syntax: 'bash' },
      node: { title: 'Node.js', syntax: 'javascript' }
    },
    defaultExpanded: true,
    languages: null
  }
};
```

### OAuth2 Configuration

```javascript
ui.initOAuth({
  clientId: 'your-client-id',
  clientSecret: 'your-client-secret',    // Don't use in production!
  realm: 'your-realm',
  appName: 'Sketchfab API',
  scopeSeparator: ' ',
  scopes: 'read write',
  additionalQueryStringParams: {},
  useBasicAuthenticationWithAccessCodeGrant: false,
  usePkceWithAuthorizationCodeGrant: true
});
```

### Custom Plugins

```javascript
// Create custom plugin
const CustomPlugin = function(system) {
  return {
    // State actions
    statePlugins: {
      custom: {
        actions: {
          setCustomValue: (value) => ({
            type: 'SET_CUSTOM_VALUE',
            payload: value
          })
        },
        reducers: {
          'SET_CUSTOM_VALUE': (state, action) => {
            return state.set('customValue', action.payload);
          }
        },
        selectors: {
          customValue: (state) => state.get('customValue')
        }
      }
    },
    
    // Custom components
    components: {
      CustomBanner: () => (
        <div className="custom-banner">
          Custom content
        </div>
      )
    },
    
    // Wrap existing components
    wrapComponents: {
      InfoContainer: (Original, system) => (props) => (
        <div>
          <CustomBanner />
          <Original {...props} />
        </div>
      )
    }
  };
};

// Use plugin
const ui = SwaggerUIBundle({
  plugins: [CustomPlugin],
  // ...
});
```

## API Structure Displayed

```yaml
# Example OpenAPI that Swagger UI renders
openapi: 3.0.0
info:
  title: Sketchfab API
  version: v3
  description: Access Sketchfab's 3D models programmatically

servers:
  - url: https://api.sketchfab.com/v3

paths:
  /models:
    get:
      summary: List models
      tags: [Models]
      parameters:
        - name: count
          in: query
          schema:
            type: integer
            default: 24
      responses:
        200:
          description: Model list
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ModelList'

  /models/{uid}:
    get:
      summary: Get model
      tags: [Models]
      parameters:
        - name: uid
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Model details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Model'

components:
  schemas:
    Model:
      type: object
      properties:
        uid:
          type: string
        name:
          type: string
        viewCount:
          type: integer
        
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://sketchfab.com/oauth2/authorize
          tokenUrl: https://sketchfab.com/oauth2/token
          scopes:
            read: Read access
            write: Write access
```

## UI Components

Swagger UI renders:

1. **API Info Header** - Title, version, description
2. **Server Selector** - Choose base URL
3. **Authentication** - OAuth2, API key buttons
4. **Tag Groups** - Operations grouped by tags
5. **Operations** - Expandable endpoint details
   - Method + Path
   - Description
   - Parameters (path, query, header, body)
   - Request body schema
   - Response schemas
   - Try it out button
6. **Models Section** - Schema definitions

## Sketchfab API Usage

```javascript
// Sketchfab uses Swagger UI for API documentation at:
// https://sketchfab.com/developers/data-api/v3

// Initialize with Sketchfab's OpenAPI spec
const ui = SwaggerUIBundle({
  url: 'https://api.sketchfab.com/v3/openapi.json',
  dom_id: '#api-docs',
  presets: [
    SwaggerUIBundle.presets.apis,
    SwaggerUIStandalonePreset
  ],
  layout: 'StandaloneLayout',
  
  // Auto-fill auth token
  onComplete: function() {
    const token = getStoredToken();
    if (token) {
      ui.preauthorizeApiKey('bearerAuth', token);
    }
  }
});
```

## CSS Customization

```css
/* Override Swagger UI styles */
.swagger-ui {
  font-family: 'Inter', sans-serif;
}

.swagger-ui .topbar {
  background-color: #1caad9;
}

.swagger-ui .info .title {
  color: #1a1a1a;
}

.swagger-ui .opblock-tag {
  border-bottom: 1px solid #e0e0e0;
}

.swagger-ui .opblock.opblock-get {
  border-color: #61affe;
  background: rgba(97, 175, 254, 0.1);
}

.swagger-ui .opblock.opblock-post {
  border-color: #49cc90;
  background: rgba(73, 204, 144, 0.1);
}

.swagger-ui .opblock.opblock-delete {
  border-color: #f93e3e;
  background: rgba(249, 62, 62, 0.1);
}

.swagger-ui .btn.execute {
  background-color: #1caad9;
}
```

## Notes

- Full Swagger/OpenAPI 3.0 specification renderer
- Interactive "Try it out" functionality
- OAuth2 authentication support
- Used for Sketchfab's Data API documentation
- Customizable with plugins and CSS
- Large bundle due to full-featured API explorer
