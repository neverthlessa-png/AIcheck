"""检测面板组件"""

from pathlib import Path
from typing import Optional

from loguru import logger
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ai_check.config.settings import settings
from ai_check.core import DetectorRegistry
from ai_check.utils.image_utils import get_image_info, load_image, compute_md5


class DetectionPanel(QWidget):
    """检测面板"""

    images_changed = pyqtSignal(int)  # 图片数量变化信号

    def __init__(self) -> None:
        super().__init__()
        self._images: list = []  # ImageInfo列表
        self._init_ui()

    def _init_ui(self) -> None:
        """初始化UI"""
        layout = QHBoxLayout(self)

        # 左侧：图片列表
        left_panel = self._create_image_list_panel()
        layout.addWidget(left_panel, 2)

        # 右侧：检测选项
        right_panel = self._create_options_panel()
        layout.addWidget(right_panel, 1)

    def _create_image_list_panel(self) -> QWidget:
        """创建图片列表面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 标题和工具栏
        header_layout = QHBoxLayout()
        header_label = QLabel("待检测图片")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # 添加图片按钮
        add_btn = QPushButton("添加图片")
        add_btn.clicked.connect(self._add_files)
        header_layout.addWidget(add_btn)

        add_folder_btn = QPushButton("添加文件夹")
        add_folder_btn.clicked.connect(self._add_folder)
        header_layout.addWidget(add_folder_btn)

        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self._clear_images)
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # 图片列表表格
        self._image_table = QTableWidget()
        self._image_table.setColumnCount(4)
        self._image_table.setHorizontalHeaderLabels(["文件名", "尺寸", "大小", "状态"])
        self._image_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._image_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        header = self._image_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self._image_table)

        # 统计信息
        self._stats_label = QLabel("共 0 张图片")
        layout.addWidget(self._stats_label)

        return panel

    def _create_options_panel(self) -> QWidget:
        """创建检测选项面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 检测器选择
        detector_group = QGroupBox("检测器选择")
        detector_layout = QVBoxLayout(detector_group)

        self._detector_checks: dict[str, QCheckBox] = {}
        for name in DetectorRegistry.list_registered():
            cb = QCheckBox(name)
            cb.setChecked(True)
            detector_layout.addWidget(cb)
            self._detector_checks[name] = cb

        # 如果没有注册的检测器，显示提示
        if not self._detector_checks:
            placeholder = QLabel("暂无可用检测器")
            placeholder.setStyleSheet("color: gray;")
            detector_layout.addWidget(placeholder)

        layout.addWidget(detector_group)

        # 性能设置
        perf_group = QGroupBox("性能设置")
        perf_layout = QVBoxLayout(perf_group)

        # 批处理大小
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("批处理大小:"))
        self._batch_size_spin = QSpinBox()
        self._batch_size_spin.setRange(1, 128)
        self._batch_size_spin.setValue(settings.batch_size)
        batch_layout.addWidget(self._batch_size_spin)
        perf_layout.addLayout(batch_layout)

        # 设备选择
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("计算设备:"))
        self._device_combo = QComboBox()
        self._device_combo.addItems(["自动", "CPU", "GPU (CUDA)"])
        device_layout.addWidget(self._device_combo)
        perf_layout.addLayout(device_layout)

        # 并行处理
        parallel_layout = QHBoxLayout()
        parallel_layout.addWidget(QLabel("并行线程:"))
        self._parallel_spin = QSpinBox()
        self._parallel_spin.setRange(1, 16)
        self._parallel_spin.setValue(4)
        parallel_layout.addWidget(self._parallel_spin)
        perf_layout.addLayout(parallel_layout)

        layout.addWidget(perf_group)

        # 输出设置
        output_group = QGroupBox("输出设置")
        output_layout = QVBoxLayout(output_group)

        self._save_results_cb = QCheckBox("保存检测结果")
        self._save_results_cb.setChecked(True)
        output_layout.addWidget(self._save_results_cb)

        self._generate_report_cb = QCheckBox("生成报告")
        self._generate_report_cb.setChecked(True)
        output_layout.addWidget(self._generate_report_cb)

        layout.addWidget(output_group)

        layout.addStretch()

        # 开始检测按钮
        self._start_btn = QPushButton("开始检测")
        self._start_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; "
            "padding: 10px; font-size: 14px; border-radius: 5px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        layout.addWidget(self._start_btn)

        return panel

    def _add_files(self) -> None:
        """添加文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;所有文件 (*)",
        )
        if files:
            self.add_files([Path(f) for f in files])

    def _add_folder(self) -> None:
        """添加文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.add_folder(Path(folder))

    def _clear_images(self) -> None:
        """清空图片列表"""
        self._images.clear()
        self._image_table.setRowCount(0)
        self._update_stats()

    def add_files(self, files: list[Path]) -> None:
        """添加文件"""
        for file_path in files:
            if file_path.is_file() and self._is_image_file(file_path):
                self._add_image(file_path)

    def add_folder(self, folder: Path) -> None:
        """添加文件夹"""
        image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp"}
        for ext in image_extensions:
            for file_path in folder.glob(f"*{ext}"):
                self._add_image(file_path)
            for file_path in folder.glob(f"*{ext.upper()}"):
                self._add_image(file_path)

    def _is_image_file(self, path: Path) -> bool:
        """检查是否是图片文件"""
        image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp"}
        return path.suffix.lower() in image_extensions

    def _add_image(self, path: Path) -> None:
        """添加单张图片"""
        try:
            info = get_image_info(path)

            row = self._image_table.rowCount()
            self._image_table.insertRow(row)
            self._image_table.setItem(row, 0, QTableWidgetItem(info["filename"]))
            self._image_table.setItem(row, 1, QTableWidgetItem(f"{info['width']}x{info['height']}"))
            self._image_table.setItem(row, 2, QTableWidgetItem(self._format_size(info["file_size"])))
            self._image_table.setItem(row, 3, QTableWidgetItem("待检测"))

            # 存储完整路径
            self._image_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(path))

            self._images.append(path)
            self._update_stats()

        except Exception as e:
            logger.warning(f"添加图片失败 {path}: {e}")

    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / 1024 / 1024:.1f} MB"

    def _update_stats(self) -> None:
        """更新统计信息"""
        self._stats_label.setText(f"共 {len(self._images)} 张图片")
        self.images_changed.emit(len(self._images))

    def get_images(self) -> list:
        """获取待检测图片列表"""
        from image_checker.core import ImageInfo

        result = []
        for path in self._images:
            try:
                image = load_image(path)
                image_info = ImageInfo(
                    path=path,
                    image=image,
                    md5_hash=compute_md5(path),
                )
                result.append(image_info)
            except Exception as e:
                logger.error(f"加载图片失败 {path}: {e}")

        return result

    def get_selected_detectors(self) -> list[str]:
        """获取选中的检测器"""
        return [name for name, cb in self._detector_checks.items() if cb.isChecked()]

    def get_batch_size(self) -> int:
        """获取批处理大小"""
        return self._batch_size_spin.value()
