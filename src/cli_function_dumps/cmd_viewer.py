# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_viewer(args):
    """Launch the 3D model viewer."""
    msgs = get_messages()['viewer']
    window_sizes = get_window_sizes() if hasattr(sys.modules[__name__], 'get_window_sizes') else {'min_width': 800, 'min_height': 600}
    try:
        from PyQt6.QtWidgets import QApplication
        from src.model_viewer import ModelViewerPanel
        import sys
    except ImportError as e:
        print(msgs['error_packages'].format(error=e))
        print(msgs['install_hint'])
        return 1

    print(msgs['launching'])

    try:
        # Create Qt application
        app = QApplication(sys.argv)

        # Create viewer window
        from PyQt6.QtWidgets import QMainWindow
        window = QMainWindow()
        window.setWindowTitle(msgs['window_title'])
        window.setMinimumSize(800, 600)

        # Create viewer panel
        viewer = ModelViewerPanel()
        window.setCentralWidget(viewer)

        # Load model if specified
        if args.binz_file:
            binz_path = Path(args.binz_file)
            if binz_path.exists():
                print(msgs['loading_model'].format(path=binz_path))
                # Look for params file
                params_path = binz_path.with_name(binz_path.stem + "_params.json")
                if not params_path.exists():
                    params_path = None

                if viewer.viewer.load_model(str(binz_path), str(params_path) if params_path else None):
                    vertex_count = viewer.viewer.geometry.vertex_count if viewer.viewer.geometry else 0
                    triangle_count = viewer.viewer.geometry.triangle_count if viewer.viewer.geometry else 0
                    viewer.info_label.setText(
                        f"Loaded: {binz_path.name} | "
                        f"Vertices: {vertex_count:,} | "
                        f"Triangles: {triangle_count:,}"
                    )
                    print(msgs['model_loaded'].format(vertices=vertex_count, triangles=triangle_count))
                else:
                    print(msgs['load_failed'].format(path=binz_path))
            else:
                print(msgs['not_found'].format(path=binz_path))

        # Show window
        window.show()

        # Run application
        return app.exec()

    except Exception as e:
        print(msgs['error_launch'].format(error=e))
        return 1
