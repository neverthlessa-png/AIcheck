"""主窗口"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from ai_check.config.settings import settings


class MainWindow:
    """主窗口应用"""

    def __init__(self) -> None:
        self._qt_app: Optional[object] = None
        self._main_window: Optional[object] = None

    def run(self) -> int:
        """运行应用"""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt

            # 创建应用
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

            self._qt_app = QApplication(sys.argv)
            self._qt_app.setApplicationName(settings.app_name)
            self._qt_app.setApplicationVersion(settings.app_version)

            # 创建主窗口
            from ai_check.app.widgets.main_window_widget import MainWindowWidget

            self._main_window = MainWindowWidget()
            self._main_window.show()

            logger.info("GUI已启动")
            return self._qt_app.exec()

        except ImportError as e:
            logger.error(f"PyQt6未安装: {e}")
            logger.info("请安装PyQt6: pip install PyQt6")
            return 1
        except Exception as e:
            logger.exception(f"GUI启动失败: {e}")
            return 1
