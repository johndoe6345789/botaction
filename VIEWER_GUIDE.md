# Sketchfab Model Viewer - Usage Guide

## 3D Model Viewer

The application now includes a built-in 3D model viewer that can display downloaded .binz models.

### Features

- **Interactive 3D Rendering**: View your downloaded Sketchfab models in real-time
- **Mouse Controls**:
  - **Left Click + Drag**: Rotate the model
  - **Mouse Wheel**: Zoom in/out
- **Rendering Options**:
  - Toggle wireframe mode
  - Reset camera view
- **Auto-loading**: Automatically finds .binz files in the downloads directory

### How to Use

1. **Download a Model**:
   - Enter a Sketchfab model URL
   - Click "Fetch" to get model information
   - Click "Download Files" to download the model data

2. **View the 3D Model**:
   - Switch to the "3D Viewer" tab
   - Click "Load Model" to load the downloaded .binz file
   - Use mouse controls to interact with the model

3. **Controls**:
   - **Load Model**: Loads the first .binz file found in the downloads directory
   - **Toggle Wireframe**: Switch between solid and wireframe rendering
   - **Reset View**: Reset camera to default position

### Requirements

The 3D viewer requires:
- PyQt6 (GUI framework)
- PyOpenGL (OpenGL bindings)
- numpy (numerical operations)

Install with:
```bash
pip install PyQt6 PyOpenGL PyOpenGL_accelerate numpy
```

### Standalone Viewer

You can also run the 3D viewer standalone:
```bash
python test_viewer.py
```

### Technical Details

The viewer uses:
- OpenGL for 3D rendering
- Immediate mode rendering (compatible with most systems)
- Automatic model centering and scaling
- Face normal computation for lighting

### Troubleshooting

**Model not loading**:
- Ensure .binz files exist in the `downloads/` directory
- Check that the file was properly downloaded
- Try downloading the model again

**Black screen or no rendering**:
- Verify OpenGL support on your system
- Check that PyOpenGL is installed correctly
- Try updating your graphics drivers

**Performance issues**:
- Large models may render slowly
- Consider reducing model complexity
- Close other applications to free up GPU resources

### File Format

The viewer reads:
- `.binz` files: Compressed binary geometry data
- `_params.json` files: Optional metadata for parsing the geometry

The .binz format contains:
- Vertex positions (vec3)
- Normals (vec3)
- Texture coordinates (vec2)
- Triangle indices

### Future Enhancements

Planned features:
- Texture support
- Multiple material rendering
- Animation playback
- Better camera controls (pan, orbit)
- Export to other formats
- Performance optimizations with VBOs
