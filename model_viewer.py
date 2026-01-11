"""
3D Model Viewer for PyQt6

Displays .binz files from Sketchfab using OpenGL.
"""

import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import json

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QMatrix4x4, QVector3D, QQuaternion

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False

from binz_reader import BinzReader, MeshGeometry

try:
    from model_decryptor import SketchfabDecryptor, CRYPTO_AVAILABLE as DECRYPTION_AVAILABLE
except ImportError:
    DECRYPTION_AVAILABLE = False


class ModelViewerWidget(QOpenGLWidget):
    """OpenGL widget for displaying 3D models."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.geometry: Optional[MeshGeometry] = None
        
        # Camera parameters
        self.rotation_x = 30.0
        self.rotation_y = 45.0
        self.zoom = 3.0
        
        # Mouse interaction
        self.last_pos = QPoint()
        self.is_rotating = False
        
        # Rendering options
        self.show_wireframe = False
        self.show_normals = False
        
        # Vertex buffer objects
        self.vbo_vertices = None
        self.vbo_normals = None
        self.vbo_indices = None
        
        # Model bounds for auto-centering
        self.model_center = np.array([0.0, 0.0, 0.0])
        self.model_scale = 1.0
        
    def load_model(self, binz_path: str, params_path: Optional[str] = None):
        """Load a .binz model file."""
        try:
            reader = BinzReader()
            
            # Try to decrypt if encrypted and params available
            if params_path and Path(params_path).exists() and DECRYPTION_AVAILABLE:
                try:
                    decryptor = SketchfabDecryptor()
                    with open(params_path, 'r') as f:
                        import json
                        params = json.load(f)
                    
                    # Check if encrypted
                    if params and isinstance(params, list) and params[0].get('d', False):
                        print("Model is encrypted, decrypting...")
                        data = decryptor.decrypt_and_decompress(binz_path, params)
                    else:
                        # Not encrypted, just decompress
                        data = reader.read_file(binz_path)
                except Exception as e:
                    print(f"Decryption failed: {e}, trying raw read...")
                    data = reader.read_file(binz_path)
            else:
                # No params or decryption not available
                data = reader.read_file(binz_path)
            
            # Try to parse the geometry
            # If we have params, use them; otherwise try to parse raw data
            if params_path and Path(params_path).exists():
                with open(params_path, 'r') as f:
                    params = json.load(f)
                self.geometry = reader.parse_geometry_from_params(data, params)
            else:
                # Try basic parsing
                self.geometry = self._parse_basic_geometry(reader, data)
            
            if self.geometry and self.geometry.vertices:
                self._compute_model_bounds()
                self._prepare_buffers()
                self.update()
                return True
            return False
            
        except Exception as e:
            print(f"Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _parse_basic_geometry(self, reader: BinzReader, data: bytes) -> MeshGeometry:
        """Parse geometry from raw binary data without params."""
        from binz_reader import GeometryBuffer
        
        geometry = MeshGeometry()
        
        # Try to intelligently guess the structure
        # Common pattern: vertices (float32 * 3 * N), then indices (uint16/32)
        
        data_len = len(data)
        # Assume first 75% is vertex data (positions + normals + uvs)
        # Last 25% is indices
        
        vertex_data_len = int(data_len * 0.75)
        
        # Try to extract vertices (vec3 positions)
        vertex_count = vertex_data_len // (4 * 3)  # float32 * 3
        vertices = reader.read_float32_array(data, 0, vertex_count * 3)
        
        if len(vertices) > 0:
            geometry.vertices = GeometryBuffer(
                data=vertices.reshape(-1, 3),
                item_size=3,
                count=vertex_count
            )
        
        # Try to extract indices from the rest
        index_offset = vertex_data_len
        remaining = data_len - index_offset
        
        # Try uint16 first
        if remaining % 2 == 0:
            try:
                indices = reader.read_uint16_array(data, index_offset)
                if len(indices) > 0 and np.max(indices) < vertex_count:
                    geometry.indices = GeometryBuffer(
                        data=indices,
                        item_size=1,
                        count=len(indices)
                    )
            except:
                pass
        
        # Try uint32 if uint16 failed
        if geometry.indices is None and remaining % 4 == 0:
            try:
                indices = reader.read_uint32_array(data, index_offset)
                if len(indices) > 0 and np.max(indices) < vertex_count:
                    geometry.indices = GeometryBuffer(
                        data=indices,
                        item_size=1,
                        count=len(indices)
                    )
            except:
                pass
        
        return geometry
    
    def _compute_model_bounds(self):
        """Compute model center and scale for auto-fitting."""
        if not self.geometry or not self.geometry.vertices:
            return
        
        vertices = self.geometry.vertices.data
        
        # Compute bounding box
        min_point = np.min(vertices, axis=0)
        max_point = np.max(vertices, axis=0)
        
        # Center
        self.model_center = (min_point + max_point) / 2.0
        
        # Scale to fit in unit cube
        extent = max_point - min_point
        max_extent = np.max(extent)
        if max_extent > 0:
            self.model_scale = 2.0 / max_extent
        else:
            self.model_scale = 1.0
    
    def _prepare_buffers(self):
        """Prepare OpenGL buffers (simplified for immediate mode)."""
        # We'll use immediate mode rendering for simplicity
        # In production, you'd want to use VBOs
        pass
    
    def initializeGL(self):
        """Initialize OpenGL context."""
        if not OPENGL_AVAILABLE:
            return
            
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up lighting
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        
        # Background color
        glClearColor(0.1, 0.1, 0.15, 1.0)
        
        # Enable smooth shading
        glShadeModel(GL_SMOOTH)
    
    def resizeGL(self, w: int, h: int):
        """Handle window resize."""
        if not OPENGL_AVAILABLE:
            return
            
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        aspect = w / h if h > 0 else 1.0
        gluPerspective(45.0, aspect, 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        """Render the scene."""
        if not OPENGL_AVAILABLE:
            return
            
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Camera positioning
        glTranslatef(0.0, 0.0, -self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
        
        # Draw grid
        self._draw_grid()
        
        # Draw model if loaded
        if self.geometry and self.geometry.vertices:
            self._draw_model()
    
    def _draw_grid(self):
        """Draw a reference grid."""
        glDisable(GL_LIGHTING)
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_LINES)
        
        size = 5
        step = 0.5
        for i in np.arange(-size, size + step, step):
            # Lines parallel to X axis
            glVertex3f(-size, 0, i)
            glVertex3f(size, 0, i)
            # Lines parallel to Z axis
            glVertex3f(i, 0, -size)
            glVertex3f(i, 0, size)
        
        glEnd()
        
        # Draw axes
        glBegin(GL_LINES)
        # X axis - red
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(1, 0, 0)
        # Y axis - green
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 1, 0)
        # Z axis - blue
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 1)
        glEnd()
        
        glEnable(GL_LIGHTING)
    
    def _draw_model(self):
        """Draw the loaded 3D model."""
        glPushMatrix()
        
        # Center and scale the model
        glScalef(self.model_scale, self.model_scale, self.model_scale)
        glTranslatef(-self.model_center[0], -self.model_center[1], -self.model_center[2])
        
        # Set material
        glColor3f(0.7, 0.7, 0.8)
        
        if self.show_wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        vertices = self.geometry.vertices.data
        
        # Draw with indices if available
        if self.geometry.indices:
            indices = self.geometry.indices.data
            
            glBegin(GL_TRIANGLES)
            for i in range(0, len(indices), 3):
                if i + 2 < len(indices):
                    idx0, idx1, idx2 = indices[i], indices[i+1], indices[i+2]
                    
                    # Check bounds
                    if idx0 < len(vertices) and idx1 < len(vertices) and idx2 < len(vertices):
                        v0, v1, v2 = vertices[idx0], vertices[idx1], vertices[idx2]
                        
                        # Compute face normal
                        edge1 = v1 - v0
                        edge2 = v2 - v0
                        normal = np.cross(edge1, edge2)
                        norm = np.linalg.norm(normal)
                        if norm > 0:
                            normal /= norm
                            glNormal3fv(normal)
                        
                        glVertex3fv(v0)
                        glVertex3fv(v1)
                        glVertex3fv(v2)
            glEnd()
        else:
            # Draw without indices (sequential triangles)
            glBegin(GL_TRIANGLES)
            for i in range(0, len(vertices) - 2, 3):
                v0, v1, v2 = vertices[i], vertices[i+1], vertices[i+2]
                
                # Compute face normal
                edge1 = v1 - v0
                edge2 = v2 - v0
                normal = np.cross(edge1, edge2)
                norm = np.linalg.norm(normal)
                if norm > 0:
                    normal /= norm
                    glNormal3fv(normal)
                
                glVertex3fv(v0)
                glVertex3fv(v1)
                glVertex3fv(v2)
            glEnd()
        
        glPopMatrix()
    
    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_pos = event.pos()
            self.is_rotating = True
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_rotating = False
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement for rotation."""
        if self.is_rotating:
            dx = event.pos().x() - self.last_pos.x()
            dy = event.pos().y() - self.last_pos.y()
            
            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5
            
            self.last_pos = event.pos()
            self.update()
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zoom."""
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom *= 0.9
        else:
            self.zoom *= 1.1
        
        self.zoom = max(1.0, min(10.0, self.zoom))
        self.update()


class ModelViewerPanel(QWidget):
    """Panel containing the 3D model viewer and controls."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        if not OPENGL_AVAILABLE:
            error_label = QLabel("OpenGL not available. Please install PyOpenGL:\npip install PyOpenGL PyOpenGL_accelerate")
            error_label.setStyleSheet("color: #ff6b6b; padding: 20px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)
            return
        
        # Viewer widget
        self.viewer = ModelViewerWidget()
        self.viewer.setMinimumSize(400, 400)
        layout.addWidget(self.viewer, stretch=1)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Load button
        self.load_btn = QPushButton("Load Model")
        self.load_btn.clicked.connect(self.load_model_from_downloads)
        controls_layout.addWidget(self.load_btn)
        
        # Wireframe toggle
        self.wireframe_btn = QPushButton("Toggle Wireframe")
        self.wireframe_btn.clicked.connect(self.toggle_wireframe)
        controls_layout.addWidget(self.wireframe_btn)
        
        # Reset view
        self.reset_btn = QPushButton("Reset View")
        self.reset_btn.clicked.connect(self.reset_view)
        controls_layout.addWidget(self.reset_btn)
        
        # Info label
        self.info_label = QLabel("No model loaded")
        controls_layout.addWidget(self.info_label, stretch=1)
        
        layout.addLayout(controls_layout)
        
    def load_model_from_downloads(self):
        """Load a model from the downloads directory."""
        downloads_dir = Path(__file__).parent / "downloads"
        if not downloads_dir.exists():
            self.info_label.setText("No downloads directory found")
            return
        
        # Find .binz files
        binz_files = list(downloads_dir.glob("*.binz"))
        if not binz_files:
            self.info_label.setText("No .binz files found in downloads/")
            return
        
        # Load the first one found
        binz_path = binz_files[0]
        
        # Look for matching params file
        params_path = binz_path.with_name(binz_path.stem + "_params.json")
        if not params_path.exists():
            params_path = None
        
        self.info_label.setText(f"Loading {binz_path.name}...")
        
        if self.viewer.load_model(str(binz_path), str(params_path) if params_path else None):
            vertex_count = self.viewer.geometry.vertex_count if self.viewer.geometry else 0
            triangle_count = self.viewer.geometry.triangle_count if self.viewer.geometry else 0
            self.info_label.setText(
                f"Loaded: {binz_path.name} | "
                f"Vertices: {vertex_count:,} | "
                f"Triangles: {triangle_count:,}"
            )
        else:
            self.info_label.setText(f"Failed to load {binz_path.name}")
    
    def toggle_wireframe(self):
        """Toggle wireframe rendering."""
        self.viewer.show_wireframe = not self.viewer.show_wireframe
        self.viewer.update()
    
    def reset_view(self):
        """Reset camera view."""
        self.viewer.rotation_x = 30.0
        self.viewer.rotation_y = 45.0
        self.viewer.zoom = 3.0
        self.viewer.update()
