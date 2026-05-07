"""主窗口组件"""

from pathlib import Path
from typing import Optional

from loguru import logger
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QProgressBar,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ai_check.config.settings import settings
from ai_check.core import DetectorRegistry, Pipeline, PipelineConfig, TaskManager


class DetectionWorker(QThread):
    """检测工作线程"""

    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(bool)  # success

    def __init__(self, pipeline: Pipeline, images: list) -> None:
        super().__init__()
        self.pipeline = pipeline
        self.images = images

    def run(self) -> None:
        try:
            total = len(self.images)
            for i, image_info in enumerate(self.images):
                self.pipeline.process_single(image_info)
                self.progress.emit(i + 1, total, f"处理: {image_info.path.name}")
            self.finished.emit(True)
        except Exception as e:
            logger.error(f"检测失败: {e}")
            self.finished.emit(False)


class MainWindowWidget(QMainWindow):
    """主窗口"""

    def __init__(self) -> None:
        super().__init__()

        self._pipeline: Optional[Pipeline] = None
        self._task_manager = TaskManager()
        self._worker: Optional[DetectionWorker] = None

        self._init_ui()
        self._init_pipeline()

    def _init_ui(self) -> None:
        """初始化UI"""
        # 窗口设置
        window_size = settings.get("gui.window_size", [1280, 800])
        self.resize(window_size[0], window_size[1])
        self.setWindowTitle(f"{settings.app_name} v{settings.app_version}")

        # 创建菜单栏
        self._create_menu_bar()

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 创建选项卡
        self._tab_widget = QTabWidget()
        layout.addWidget(self._tab_widget)

        # 添加选项卡页面
        self._create_detection_tab()
        self._create_result_tab()
        self._create_settings_tab()

        # 创建状态栏
        self._create_status_bar()

    def _create_menu_bar(self) -> None:
        """创建菜单栏"""
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        # 文件菜单
        file_menu = QMenu("文件(&F)", self)
        menu_bar.addMenu(file_menu)

        open_action = QAction("打开图片(&O)", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_files)
        file_menu.addAction(open_action)

        open_folder_action = QAction("打开文件夹(&D)", self)
        open_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_folder_action.triggered.connect(self._open_folder)
        file_menu.addAction(open_folder_action)

        file_menu.addSeparator()

        export_action = QAction("导出报告(&E)", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self._export_report)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 检测菜单
        detect_menu = QMenu("检测(&D)", self)
        menu_bar.addMenu(detect_menu)

        start_action = QAction("开始检测(&S)", self)
        start_action.setShortcut(QKeySequence("F5"))
        start_action.triggered.connect(self._start_detection)
        detect_menu.addAction(start_action)

        stop_action = QAction("停止检测(&T)", self)
        stop_action.setShortcut(QKeySequence("Shift+F5"))
        stop_action.triggered.connect(self._stop_detection)
        detect_menu.addAction(stop_action)

        # 帮助菜单
        help_menu = QMenu("帮助(&H)", self)
        menu_bar.addMenu(help_menu)

        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_detection_tab(self) -> None:
        """创建检测选项卡"""
        from ai_check.app.widgets.detection_panel import DetectionPanel

        self._detection_panel = DetectionPanel()
        self._tab_widget.addTab(self._detection_panel, "检测")

    def _create_result_tab(self) -> None:
        """创建结果选项卡"""
        from ai_check.app.widgets.result_viewer import ResultViewer

        self._result_viewer = ResultViewer()
        self._tab_widget.addTab(self._result_viewer, "结果")

    def _create_settings_tab(self) -> None:
        """创建设置选项卡"""
        from ai_check.app.widgets.settings_dialog import SettingsPanel

        self._settings_panel = SettingsPanel()
        self._tab_widget.addTab(self._settings_panel, "设置")

    def _create_status_bar(self) -> None:
        """创建状态栏"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        self._status_label = QLabel("就绪")
        status_bar.addWidget(self._status_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        status_bar.addPermanentWidget(self._progress_bar)

    def _init_pipeline(self) -> None:
        """初始化检测流水线"""
        try:
            # 导入并注册检测器
            from ai_check.detectors.forgery.ps_detector import PSDetector
            from ai_check.detectors.duplicate.hash_detector import HashDetector

            # 创建流水线
            config = PipelineConfig(
                enabled_detectors=["ps_detector", "hash_detector"],
                max_workers=4,
            )
            self._pipeline = Pipeline(config)

            # 添加检测器
            self._pipeline.add_detector(PSDetector())
            self._pipeline.add_detector(HashDetector())

            # 初始化
            self._pipeline.initialize()

            logger.info("检测流水线初始化完成")

        except Exception as e:
            logger.error(f"检测流水线初始化失败: {e}")

    def _open_files(self) -> None:
        """打开文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*)",
        )
        if files:
            self._detection_panel.add_files([Path(f) for f in files])

    def _open_folder(self) -> None:
        """打开文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self._detection_panel.add_folder(Path(folder))

    def _export_report(self) -> None:
        """导出报告"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存报告",
            "",
            "Excel文件 (*.xlsx);;CSV文件 (*.csv)",
        )
        if file_path:
            self._result_viewer.export_report(Path(file_path))

    def _start_detection(self) -> None:
        """开始检测"""
        if self._pipeline is None:
            logger.error("检测流水线未初始化")
            return

        images = self._detection_panel.get_images()
        if not images:
            logger.warning("没有待检测的图片")
            return

        self._status_label.setText("检测中...")
        self._progress_bar.setVisible(True)
        self._progress_bar.setMaximum(len(images))
        self._progress_bar.setValue(0)

        # 创建工作线程
        self._worker = DetectionWorker(self._pipeline, images)
        self._worker.progress.connect(self._on_detection_progress)
        self._worker.finished.connect(self._on_detection_finished)
        self._worker.start()

    def _stop_detection(self) -> None:
        """停止检测"""
        if self._worker and self._worker.isRunning():
            self._worker.terminate()
            self._status_label.setText("已停止")
            self._progress_bar.setVisible(False)

    def _on_detection_progress(self, current: int, total: int, message: str) -> None:
        """检测进度回调"""
        self._progress_bar.setValue(current)
        self._status_label.setText(message)

    def _on_detection_finished(self, success: bool) -> None:
        """检测完成回调"""
        self._progress_bar.setVisible(False)
        if success:
            self._status_label.setText("检测完成")
        else:
            self._status_label.setText("检测失败")
        self._worker = None

    def _show_about(self) -> None:
        """显示关于对话框"""
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            f"关于 {settings.app_name}",
            f"{settings.app_name} v{settings.app_version}\n\n"
            "图片AI检查工具\n"
            "支持伪造检测、重复检测、内容分析等功能",
        )

    def closeEvent(self, event) -> None:
        """关闭事件"""
        # 停止检测
        if self._worker and self._worker.isRunning():
            self._worker.terminate()

        # 清理流水线
        if self._pipeline:
            self._pipeline.cleanup()

        logger.info("应用已关闭")
        event.accept()
