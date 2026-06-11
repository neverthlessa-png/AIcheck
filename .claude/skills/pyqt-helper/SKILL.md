# PyQt Helper Skill

Assist with PyQt6 GUI development for the AI Check project.

## Trigger

Use this skill when:
- Creating new GUI components
- Fixing UI issues
- Implementing signal/slot connections
- Handling threading in GUI

## Instructions

### Basic Widget Structure

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class MyWidget(QWidget):
    """Custom widget with proper structure."""

    # Define signals
    clicked = pyqtSignal()
    data_changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        self.label = QLabel("Hello")
        self.button = QPushButton("Click")

        layout.addWidget(self.label)
        layout.addWidget(self.button)

    def _connect_signals(self):
        """Connect signals to slots."""
        self.button.clicked.connect(self._on_button_clicked)

    def _on_button_clicked(self):
        """Handle button click."""
        self.clicked.emit()
```

### Threading Pattern

For long-running operations, use QThread:

```python
from PyQt6.QtCore import QThread, pyqtSignal

class Worker(QThread):
    """Background worker thread."""

    # Signals for communication
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(object)     # result
    error = pyqtSignal(str)           # error message

    def __init__(self, data):
        super().__init__()
        self._data = data
        self._cancelled = False

    def run(self):
        """Execute in background thread."""
        try:
            total = len(self._data)
            results = []

            for i, item in enumerate(self._data):
                if self._cancelled:
                    return

                # Process item
                result = self._process(item)
                results.append(result)

                # Report progress
                self.progress.emit(i + 1, total)

            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        """Cancel the operation."""
        self._cancelled = True

    def _process(self, item):
        """Process single item."""
        ...
```

Using the worker:

```python
class MainWindow(QMainWindow):
    def start_processing(self):
        self.worker = Worker(self.data)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def on_finished(self, results):
        self.status_label.setText(f"Done: {len(results)} items")

    def on_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
        event.accept()
```

### Common Patterns

#### Progress Bar

```python
from PyQt6.QtWidgets import QProgressBar, QStatusBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Status bar with progress
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
```

#### Table Widget

```python
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

def setup_table(self):
    self.table = QTableWidget()
    self.table.setColumnCount(4)
    self.table.setHorizontalHeaderLabels(["Name", "Type", "Status", "Action"])

    # Stretch first column
    header = self.table.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

    # Selection behavior
    self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    # Add row
    row = self.table.rowCount()
    self.table.insertRow(row)
    self.table.setItem(row, 0, QTableWidgetItem("Item Name"))
```

#### Dialog

```python
from PyQt6.QtWidgets import QDialog, QDialogButtonBox

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Add widgets
        ...

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
```

### Best Practices

1. **Never block the main thread** - Use QThread for long operations
2. **Clean up resources** - Override closeEvent
3. **Use signals for communication** - Between threads and widgets
4. **Set object names** - For debugging with `obj.objectName()`
5. **Use Qt properties** - For settings binding

## Example Usage

```
Create a DetectionPanel widget for the main window:
1. Left side: image list with add/remove buttons
2. Right side: detection options (detector checkboxes, threshold slider)
3. Progress bar at bottom
4. Signal emitted when images are added
```
