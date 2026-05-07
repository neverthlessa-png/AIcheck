"""数据库管理模块"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from loguru import logger
import sqlite3


class Database:
    """SQLite数据库管理"""

    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_database(self) -> None:
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 检测结果表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detection_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                image_hash TEXT,
                detector_name TEXT NOT NULL,
                result_type TEXT NOT NULL,
                is_anomaly BOOLEAN DEFAULT 0,
                confidence REAL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 图片信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                file_size INTEGER,
                width INTEGER,
                height INTEGER,
                format TEXT,
                md5_hash TEXT,
                phash TEXT,
                feature_vector BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 检测任务表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detection_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                total_images INTEGER DEFAULT 0,
                processed_images INTEGER DEFAULT 0,
                config TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 检测器配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detector_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                config TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_image ON detection_results(image_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_detector ON detection_results(detector_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_images_hash ON images(md5_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_images_phash ON images(phash)")

        conn.commit()
        logger.info(f"数据库初始化完成: {self.db_path}")

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """执行SQL语句"""
        conn = self._get_connection()
        return conn.execute(query, params)

    def insert_detection_result(
        self,
        image_path: str,
        detector_name: str,
        result_type: str,
        is_anomaly: bool = False,
        confidence: float = 0.0,
        details: dict[str, Any] | None = None,
        image_hash: str | None = None,
    ) -> int:
        """插入检测结果"""
        cursor = self.execute(
            """
            INSERT INTO detection_results
            (image_path, image_hash, detector_name, result_type, is_anomaly, confidence, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                image_path,
                image_hash,
                detector_name,
                result_type,
                is_anomaly,
                confidence,
                json.dumps(details) if details else None,
            ),
        )
        self._get_connection().commit()
        return cursor.lastrowid

    def get_detection_results(
        self,
        image_path: str | None = None,
        detector_name: str | None = None,
        is_anomaly: bool | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """查询检测结果"""
        query = "SELECT * FROM detection_results WHERE 1=1"
        params: list[Any] = []

        if image_path:
            query += " AND image_path = ?"
            params.append(image_path)
        if detector_name:
            query += " AND detector_name = ?"
            params.append(detector_name)
        if is_anomaly is not None:
            query += " AND is_anomaly = ?"
            params.append(is_anomaly)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.execute(query, tuple(params))
        rows = cursor.fetchall()

        results = []
        for row in rows:
            result = dict(row)
            if result.get("details"):
                result["details"] = json.loads(result["details"])
            results.append(result)

        return results

    def insert_image(
        self,
        path: str,
        filename: str,
        file_size: int,
        width: int,
        height: int,
        format: str,
        md5_hash: str,
        phash: str | None = None,
    ) -> int:
        """插入图片信息"""
        cursor = self.execute(
            """
            INSERT OR REPLACE INTO images
            (path, filename, file_size, width, height, format, md5_hash, phash, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (path, filename, file_size, width, height, format, md5_hash, phash),
        )
        self._get_connection().commit()
        return cursor.lastrowid

    def get_image_by_hash(self, md5_hash: str) -> dict[str, Any] | None:
        """通过MD5哈希查找图片"""
        cursor = self.execute("SELECT * FROM images WHERE md5_hash = ?", (md5_hash,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_duplicate_images(self, phash: str) -> list[dict[str, Any]]:
        """查找相似图片（通过感知哈希）"""
        cursor = self.execute("SELECT * FROM images WHERE phash = ?", (phash,))
        return [dict(row) for row in cursor.fetchall()]

    def update_feature_vector(self, image_id: int, feature_vector: bytes) -> None:
        """更新图片的特征向量"""
        self.execute(
            "UPDATE images SET feature_vector = ? WHERE id = ?",
            (feature_vector, image_id),
        )
        self._get_connection().commit()

    def create_task(
        self,
        name: str,
        total_images: int = 0,
        config: dict[str, Any] | None = None,
    ) -> int:
        """创建检测任务"""
        cursor = self.execute(
            """
            INSERT INTO detection_tasks (name, total_images, config)
            VALUES (?, ?, ?)
            """,
            (name, total_images, json.dumps(config) if config else None),
        )
        self._get_connection().commit()
        return cursor.lastrowid

    def update_task_status(
        self,
        task_id: int,
        status: str,
        processed_images: int | None = None,
    ) -> None:
        """更新任务状态"""
        if processed_images is not None:
            self.execute(
                """
                UPDATE detection_tasks
                SET status = ?, processed_images = ?
                WHERE id = ?
                """,
                (status, processed_images, task_id),
            )
        else:
            self.execute(
                "UPDATE detection_tasks SET status = ? WHERE id = ?",
                (status, task_id),
            )

        if status == "running":
            self.execute(
                "UPDATE detection_tasks SET started_at = CURRENT_TIMESTAMP WHERE id = ?",
                (task_id,),
            )
        elif status in ("completed", "failed", "cancelled"):
            self.execute(
                "UPDATE detection_tasks SET completed_at = CURRENT_TIMESTAMP WHERE id = ?",
                (task_id,),
            )

        self._get_connection().commit()

    def close(self) -> None:
        """关闭数据库连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
