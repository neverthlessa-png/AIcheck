"""设置面板组件"""

from pathlib import Path

from loguru import logger
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ai_check.config.settings import settings


class SettingsPanel(QWidget):
    """设置面板"""

    def __init__(self) -> None:
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 常规设置
        general_group = QGroupBox("常规设置")
        general_layout = QVBoxLayout(general_group)

        # 语言
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("界面语言:"))
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(["简体中文", "English"])
        lang_layout.addWidget(self._lang_combo)
        lang_layout.addStretch()
        general_layout.addLayout(lang_layout)

        # 主题
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("界面主题:"))
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["浅色", "深色"])
        theme_layout.addWidget(self._theme_combo)
        theme_layout.addStretch()
        general_layout.addLayout(theme_layout)

        layout.addWidget(general_group)

        # 检测设置
        detection_group = QGroupBox("检测设置")
        detection_layout = QVBoxLayout(detection_group)

        # 默认阈值
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("默认置信度阈值:"))
        self._threshold_spin = QSpinBox()
        self._threshold_spin.setRange(0, 100)
        self._threshold_spin.setValue(int(settings.get("detection.confidence_threshold", 0.5) * 100))
        self._threshold_spin.setSuffix("%")
        threshold_layout.addWidget(self._threshold_spin)
        threshold_layout.addStretch()
        detection_layout.addLayout(threshold_layout)

        # 图片大小
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("处理图片尺寸:"))
        self._image_size_spin = QSpinBox()
        self._image_size_spin.setRange(128, 2048)
        self._image_size_spin.setValue(settings.get("detection.image_size", 512))
        self._image_size_spin.setSingleStep(128)
        size_layout.addWidget(self._image_size_spin)
        size_layout.addStretch()
        detection_layout.addLayout(size_layout)

        layout.addWidget(detection_group)

        # 存储设置
        storage_group = QGroupBox("存储设置")
        storage_layout = QVBoxLayout(storage_group)

        # 数据目录
        data_dir_layout = QHBoxLayout()
        data_dir_layout.addWidget(QLabel("数据目录:"))
        self._data_dir_edit = QLineEdit(str(settings.data_dir))
        data_dir_layout.addWidget(self._data_dir_edit)
        data_dir_btn = QPushButton("浏览")
        data_dir_btn.clicked.connect(self._browse_data_dir)
        data_dir_layout.addWidget(data_dir_btn)
        storage_layout.addLayout(data_dir_layout)

        # 模型目录
        model_dir_layout = QHBoxLayout()
        model_dir_layout.addWidget(QLabel("模型目录:"))
        self._model_dir_edit = QLineEdit(str(settings.models_dir))
        model_dir_layout.addWidget(self._model_dir_edit)
        model_dir_btn = QPushButton("浏览")
        model_dir_btn.clicked.connect(self._browse_model_dir)
        model_dir_layout.addWidget(model_dir_btn)
        storage_layout.addLayout(model_dir_layout)

        # 缓存大小
        cache_layout = QHBoxLayout()
        cache_layout.addWidget(QLabel("缓存大小上限:"))
        self._cache_size_spin = QSpinBox()
        self._cache_size_spin.setRange(100, 10240)
        self._cache_size_spin.setValue(settings.get("storage.cache.max_size_mb", 1024))
        self._cache_size_spin.setSuffix(" MB")
        cache_layout.addWidget(self._cache_size_spin)
        cache_layout.addStretch()
        storage_layout.addLayout(cache_layout)

        layout.addWidget(storage_group)

        # 性能设置
        perf_group = QGroupBox("性能设置")
        perf_layout = QVBoxLayout(perf_group)

        # 批处理大小
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("默认批处理大小:"))
        self._batch_size_spin = QSpinBox()
        self._batch_size_spin.setRange(1, 128)
        self._batch_size_spin.setValue(settings.batch_size)
        batch_layout.addWidget(self._batch_size_spin)
        batch_layout.addStretch()
        perf_layout.addLayout(batch_layout)

        # 线程数
        thread_layout = QHBoxLayout()
        thread_layout.addWidget(QLabel("并行线程数:"))
        self._thread_spin = QSpinBox()
        self._thread_spin.setRange(1, 16)
        self._thread_spin.setValue(4)
        thread_layout.addWidget(self._thread_spin)
        thread_layout.addStretch()
        perf_layout.addLayout(thread_layout)

        layout.addWidget(perf_group)

        layout.addStretch()

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)

        reset_btn = QPushButton("恢复默认")
        reset_btn.clicked.connect(self._reset_settings)
        button_layout.addWidget(reset_btn)

        layout.addLayout(button_layout)

    def _browse_data_dir(self) -> None:
        """浏览数据目录"""
        from PyQt6.QtWidgets import QFileDialog

        folder = QFileDialog.getExistingDirectory(self, "选择数据目录")
        if folder:
            self._data_dir_edit.setText(folder)

    def _browse_model_dir(self) -> None:
        """浏览模型目录"""
        from PyQt6.QtWidgets import QFileDialog

        folder = QFileDialog.getExistingDirectory(self, "选择模型目录")
        if folder:
            self._model_dir_edit.setText(folder)

    def _save_settings(self) -> None:
        """保存设置"""
        try:
            settings.set("detection.confidence_threshold", self._threshold_spin.value() / 100)
            settings.set("detection.image_size", self._image_size_spin.value())
            settings.set("detection.batch_size", self._batch_size_spin.value())
            settings.set("storage.cache.max_size_mb", self._cache_size_spin.value())
            settings.set("gui.theme", "dark" if self._theme_combo.currentIndex() == 1 else "light")

            logger.info("设置已保存")

        except Exception as e:
            logger.error(f"保存设置失败: {e}")

    def _reset_settings(self) -> None:
        """恢复默认设置"""
        self._threshold_spin.setValue(50)
        self._image_size_spin.setValue(512)
        self._batch_size_spin.setValue(32)
        self._thread_spin.setValue(4)
        self._cache_size_spin.setValue(1024)
        self._theme_combo.setCurrentIndex(0)
        self._lang_combo.setCurrentIndex(0)

        logger.info("已恢复默认设置")
