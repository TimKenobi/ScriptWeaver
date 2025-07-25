# app/gui/style.py

# This file contains the QSS (Qt Style Sheet) for the application.
# It defines a modern dark theme.

STYLESHEET = """
/* ------------------- General ------------------- */
QWidget {
    background-color: #2c313c;
    color: #e0e0e0;
    font-family: -apple-system, "system-ui", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 14px;
}

/* ------------------- Main Window & Dialogs ------------------- */
QMainWindow, QDialog {
    background-color: #2c313c;
}

/* ------------------- Labels ------------------- */
QLabel {
    background-color: transparent;
    color: #e0e0e0;
}

QLabel#WelcomeLabel { /* Specific style for the welcome label */
    font-size: 22px;
    font-weight: bold;
}

/* ------------------- Buttons ------------------- */
QPushButton {
    background-color: #4a5160;
    color: #e0e0e0;
    border: 1px solid #5a6170;
    padding: 8px 16px;
    border-radius: 4px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #5a6170;
    border-color: #6a7180;
}

QPushButton:pressed {
    background-color: #3e4450;
}

QPushButton:disabled {
    background-color: #3a404c;
    color: #808080;
    border-color: #4a5160;
}

/* Style for the main 'Save' button */
QPushButton#SaveButton {
    background-color: #3d84b8; /* A nice blue accent */
    font-weight: bold;
}
QPushButton#SaveButton:hover {
    background-color: #4a9dcf;
}
QPushButton#SaveButton:pressed {
    background-color: #3675a3;
}

/* ------------------- Input Fields ------------------- */
QLineEdit, QTextEdit, QSpinBox {
    background-color: #343944;
    border: 1px solid #4a5160;
    border-radius: 4px;
    padding: 5px;
    color: #e0e0e0;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
    border: 1px solid #50a1f0; /* Highlight on focus */
}

/* ------------------- List & Tab Widgets ------------------- */
QListWidget {
    background-color: #343944;
    border: 1px solid #4a5160;
    border-radius: 4px;
}

QListWidget::item {
    padding: 8px;
}

QListWidget::item:hover {
    background-color: #4a5160;
}

QListWidget::item:selected {
    background-color: #50a1f0;
    color: #ffffff;
}

QTabWidget::pane {
    border: 1px solid #4a5160;
    border-radius: 4px;
    padding: 5px;
}

QTabBar::tab {
    background-color: #343944;
    color: #e0e0e0;
    border: 1px solid #4a5160;
    border-bottom: none;
    padding: 8px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:hover {
    background-color: #4a5160;
}

QTabBar::tab:selected {
    background-color: #2c313c;
    border-color: #4a5160;
    border-bottom: 1px solid #2c313c; /* Hides bottom border */
}

/* ------------------- Other Widgets ------------------- */
QGroupBox {
    border: 1px solid #4a5160;
    border-radius: 4px;
    margin-top: 10px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    left: 10px;
}

QScrollBar:vertical {
    background: #2c313c;
    width: 12px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #4a5160;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background: #2c313c;
    height: 12px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #4a5160;
    min-width: 20px;
    border-radius: 6px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

QMessageBox {
    background-color: #343944;
}
"""
