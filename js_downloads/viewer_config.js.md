# viewer_config.js

## Overview
Sketchfab 3D viewer configuration options module containing a comprehensive JSON schema of all available viewer parameters and settings.

## File Status
- **Type**: Minified Sketchfab Webpack Bundle
- **Webpack Chunk ID**: 1287
- **Source Map**: `a261e...js.map`

## Key Components

### Configuration Schema
Contains JSON.parse of viewer configuration parameters:

#### Animation Settings
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `animation_autoplay` | bool | true | Auto-play animations on viewer start |
| `annotation` | number | 0 | Load specific annotation (1-50) on start |
| `annotation_cycle` | number | null | Autopilot cycle duration in seconds |
| `annotations_visible` | bool | null | Show/hide annotations |

#### Camera Controls
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `camera` | bool | true | Enable initial camera animation |
| `camera_constraints` | bool | true | Enable camera limits |
| `camera_easing` | number | null | Camera easing (0 = no easing) |
| `camera_eye` | vec3 | null | Force camera position |
| `camera_target` | vec3 | null | Force camera target |
| `orbit_constraint_pan` | bool | null | Disable panning |
| `orbit_constraint_pitch_down/up` | number | null | Pitch limits |
| `orbit_constraint_yaw_left/right` | number | null | Yaw limits |
| `orbit_constraint_zoom_in/out` | number | null | Zoom limits |

#### Rendering Options
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `allow_swift_shader` | bool | false | Allow software rendering |
| `anisotropy` | bool | true | Enable anisotropic filtering |
| `continuous_render` | bool | false | Redraw continuously |
| `drs` | bool | true | Dynamic resolution scaling |
| `float_rtt` | number | 2 | Render target format |
| `fxaa` | bool | null | Fast approximate anti-aliasing |
| `max_texture_size` | number | 8192 | Maximum texture resolution |
| `shadow` | bool | true | Enable shadows |
| `taa` | bool | null | Temporal anti-aliasing |
| `webgl2` | bool | true | Use WebGL 2.0 |

#### VR/AR Settings
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cardboard` | number | 0 | Start in VR mode |
| `vr_mirror` | bool | false | Mirror VR view on desktop |
| `vr_quality` | number | null | VR quality ratio |
| `arkit` | bool | false | Initialize ARKit mode |
| `vr_stereo` | bool | true | Enable stereo view |

#### UI Options
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ui_animations` | bool | true | Show animation controls |
| `ui_annotations` | bool | true | Show annotation controls |
| `ui_ar` | bool | true | Show AR button |
| `ui_controls` | bool | true | Show viewer controls |
| `ui_fullscreen` | bool | true | Show fullscreen button |
| `ui_watermark` | bool | true | Show watermark |
| `ui_theme` | string | null | UI theme (dark) |

#### Performance Options
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pixel_budget` | number | null | Pixel count limit |
| `max_device_pixel_ratio` | number | 1.5 | Maximum DPR |
| `quality` | number | null | Overall quality level |
| `graph_optimizer` | bool | null | Mesh optimization |

## Share Levels
- `private`: Internal use only
- `public`: Exposed to embed URLs
- `shared`: Common across contexts
- `limited_to`: Restricted to specific plans (pro, prem, staff)

## Dependencies
- Webpack runtime
- JSON parser

## Technical Details
- Comprehensive viewer configuration (~200+ options)
- Type validation for each parameter
- Default values and valid ranges specified
- Help text for documentation
- Alias support for legacy parameters

## Use Cases
1. Embed URL parameter configuration
2. Editor settings panel
3. API initialization options
4. VR/AR mode configuration
5. Performance tuning

## Notes
- Many options are Pro/Premium plan exclusive
- Some parameters are staff-only for debugging
- Configuration drives entire viewer behavior
- URL parameters override default values
