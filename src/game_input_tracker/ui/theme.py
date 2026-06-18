from __future__ import annotations


STYLE_SHEET = """
QWidget {
    background: #0b0f14;
    color: #f5f7fb;
    font-family: "Segoe UI";
    font-size: 10pt;
}
QMainWindow, QDialog {
    background: #0b0f14;
}
QFrame[panel="true"] {
    background: #131922;
    border: 1px solid #263241;
    border-radius: 8px;
}
QLabel[muted="true"] {
    color: #91a1b5;
}
QLabel[metric="true"] {
    color: #f8fbff;
    font-size: 22pt;
    font-weight: 700;
}
QLabel[title="true"] {
    font-size: 16pt;
    font-weight: 700;
}
QLabel[brand="true"] {
    color: #7dd3fc;
    font-size: 24pt;
    font-weight: 800;
}
QPushButton {
    background: #0369a1;
    border: 0;
    border-radius: 6px;
    color: #f8fbff;
    font-weight: 600;
    padding: 8px 12px;
}
QPushButton:hover {
    background: #0284c7;
}
QPushButton:checked {
    background: #f59e0b;
    color: #111827;
}
QTableWidget {
    background: #121923;
    border: 1px solid #263241;
    border-radius: 8px;
    gridline-color: #243142;
    selection-background-color: #0e7490;
}
QHeaderView::section {
    background: #1b2532;
    border: 0;
    color: #d6e2ef;
    padding: 7px;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
}
QCheckBox::indicator:checked {
    background: #22d3ee;
    border: 1px solid #67e8f9;
}
QScrollArea {
    border: 0;
}
"""
