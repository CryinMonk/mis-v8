import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from app.ui.login_window import MainApplication
from app.utils.logger import Logger

if __name__ == "__main__":
    # Configure logging
    logger = Logger()

    try:
        # Ensure the app runs on high DPI displays correctly
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        app = QApplication(sys.argv)
        app.setApplicationName("Management Information System")
        app.setApplicationVersion("1.0.0")

        # Create and show the main application window
        main_app = MainApplication()

        # Start the event loop
        exit_code = app.exec_()
        logger.info(f"Application exited with code: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"Unhandled exception in main: {str(e)}")
        # If we get here, something went very wrong
        if 'app' in locals():
            QMessageBox.critical(None, "Critical Error",
                                 f"An unexpected error occurred:\n\n{str(e)}\n\nThe application will now exit.")
        print(f"Critical error: {str(e)}")
        sys.exit(1)