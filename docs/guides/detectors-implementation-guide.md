# 检测器实现指南

本文档详细说明图中 9 个检测器的实现方法，包含技术选型、代码示例和集成步骤。

---

## 目录结构

```
detectors/
├── basic/                    # 基础校验
│   ├── watermark_detector.py # 图片标签/水印检测
│   ├── time_validator.py     # 时间校验
│   ├── location_validator.py # 地点校验
│   └── quality_checker.py    # 图片质量校验
├── content/                  # 内容校验
│   ├── object_validator.py   # 物体识别校验
│   └── text_validator.py     # 文字识别校验
└── advanced/                 # 高级校验
    ├── ai_generator_detector.py  # AI 生成检测
    ├── ps_forgery_detector.py    # PS 伪造检测
    └── duplicate_detector.py     # 重复图片检测
```

---

## 一、基础校验模块

### 1.1 图片标签/水印检测

**功能**: 检测图片是否包含特定标签、水印

**技术方案**:

| 方案 | 技术 | 优点 | 缺点 | 推荐场景 |
|------|------|------|------|----------|
| OCR 检测 | PaddleOCR | 可识别文字水印，准确率高 | 无法检测图形水印 | 文字水印 |
| 模板匹配 | OpenCV matchTemplate | 速度快，适合固定位置水印 | 只能检测已知水印 | 固定位置水印 |
| 深度学习 | YOLOv8 | 可检测任意水印 | 需要训练数据 | 复杂水印 |

**推荐路线**: OCR 检测 (PaddleOCR) + 模板匹配

#### 实现代码

```python
# detectors/basic/watermark_detector.py
"""
图片标签/水印检测器
- 使用 PaddleOCR 检测文字水印
- 使用 OpenCV 模板匹配检测图形水印
"""

import cv2
import numpy as np
from paddleocr import PaddleOCR
from typing import List, Dict, Any
from ai_check.core import DetectorBase, DetectionResult, DetectionType


class WatermarkDetector(DetectorBase):
    """水印检测器"""
    
    def __init__(self, name="watermark_detector", config=None):
        super().__init__(name, DetectionType.BASIC, config)
        self.ocr = None
        self.watermark_templates = []  # 水印模板图片
    
    def _initialize(self) -> bool:
        """初始化 OCR 引擎"""
        try:
            # 延迟加载 PaddleOCR
            self.ocr = PaddleOCR(
                use_angle_cls=True, 
                lang='ch',
                show_log=False
            )
            return True
        except Exception as e:
            self._logger.error(f"Failed to initialize PaddleOCR: {e}")
            return False
    
    def add_watermark_template(self, template_path: str, name: str):
        """添加水印模板"""
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is not None:
            self.watermark_templates.append({
                'name': name,
                'image': template
            })
    
    def _detect_ocr_watermark(self, image: np.ndarray) -> Dict[str, Any]:
        """使用 OCR 检测文字水印"""
        result = self.ocr.ocr(image, cls=True)
        
        # 常见水印关键词
        watermark_keywords = [
            '水印', '版权所有', 'Copyright', '©', '®',
            '样张', 'sample', 'demo', '测试',
            '严禁外传', '保密', '内部资料'
        ]
        
        detected_texts = []
        matched_keywords = []
        
        if result and result[0]:
            for line in result[0]:
                if line:
                    text = line[1][0]
                    confidence = line[1][1]
                    detected_texts.append({
                        'text': text,
                        'confidence': confidence,
                        'position': line[0]
                    })
                    
                    # 检查是否匹配水印关键词
                    for keyword in watermark_keywords:
                        if keyword.lower() in text.lower():
                            matched_keywords.append({
                                'keyword': keyword,
                                'text': text,
                                'confidence': confidence
                            })
        
        return {
            'has_text_watermark': len(matched_keywords) > 0,
            'detected_texts': detected_texts,
            'matched_keywords': matched_keywords,
            'confidence': max([m['confidence'] for m in matched_keywords], default=0)
        }
    
    def _detect_template_watermark(self, image: np.ndarray) -> Dict[str, Any]:
        """使用模板匹配检测图形水印"""
        results = []
        
        for template_info in self.watermark_templates:
            template = template_info['image']
            h, w = template.shape[:2]
            
            # 模板匹配
            res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            loc = np.where(res >= threshold)
            
            # 查找匹配位置
            points = list(zip(*loc[::-1]))
            if points:
                results.append({
                    'name': template_info['name'],
                    'positions': points,
                    'confidence': float(res[points[0]])
                })
        
        return {
            'has_template_watermark': len(results) > 0,
            'matched_templates': results,
            'confidence': max([r['confidence'] for r in results], default=0)
        }
    
    def _detect(self, image_info) -> DetectionResult:
        """执行水印检测"""
        image = image_info.image if hasattr(image_info, 'image') else cv2.imread(image_info.path)
        
        if image is None:
            return DetectionResult(
                detector_name=self._name,
                detection_type=self._detection_type,
                is_anomaly=False,
                confidence=0.0,
                description="无法加载图片"
            )
        
        # OCR 检测
        ocr_result = self._detect_ocr_watermark(image)
        
        # 模板匹配检测
        template_result = self._detect_template_watermark(image)
        
        # 综合判断
        has_watermark = ocr_result['has_text_watermark'] or template_result['has_template_watermark']
        confidence = max(ocr_result['confidence'], template_result['confidence'])
        
        description_parts = []
        if ocr_result['has_text_watermark']:
            keywords = [m['keyword'] for m in ocr_result['matched_keywords']]
            description_parts.append(f"检测到文字水印：{', '.join(keywords)}")
        if template_result['has_template_watermark']:
            names = [t['name'] for t in template_result['matched_templates']]
            description_parts.append(f"检测到图形水印：{', '.join(names)}")
        
        return DetectionResult(
            detector_name=self._name,
            detection_type=self._detection_type,
            is_anomaly=has_watermark,
            confidence=confidence,
            description="; ".join(description_parts) if description_parts else "未检测到水印",
            details={
                'ocr_result': ocr_result,
                'template_result': template_result
            }
        )
```

#### 依赖配置

```txt
# requirements.txt
paddlepaddle>=2.5.0
paddleocr>=2.7.0
opencv-python>=4.8.0
```

---

### 1.2 时间校验

**功能**: 验证图片时间信息是否吻合（EXIF 时间、图片内容时间与描述对比）

**技术方案**:

| 校验维度 | 技术 | 实现难度 |
|----------|------|----------|
| EXIF 时间提取 | PIL/Pillow | 简单 |
| 时间格式识别 | 正则 + OCR | 中等 |
| 时间逻辑验证 | 规则引擎 | 简单 |

#### 实现代码

```python
# detectors/basic/time_validator.py
"""
时间校验器
- 提取 EXIF 拍摄时间
- OCR 识别图片中可见时间
- 与描述时间对比验证
"""

from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from dateutil import parser as date_parser
import cv2
import re
from typing import Optional, Dict, Any
from paddleocr import PaddleOCR
from ai_check.core import DetectorBase, DetectionResult, DetectionType


class TimeValidator(DetectorBase):
    """时间校验器"""
    
    def __init__(self, name="time_validator", config=None):
        super().__init__(name, DetectionType.BASIC, config)
        self.ocr = None
    
    def _initialize(self) -> bool:
        """初始化 OCR 引擎"""
        try:
            self.ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
            return True
        except Exception as e:
            self._logger.error(f"Failed to initialize PaddleOCR: {e}")
            return False
    
    def _extract_exif_time(self, image_path: str) -> Optional[datetime]:
        """从 EXIF 获取拍摄时间"""
        try:
            with Image.open(image_path) as img:
                exif = img._getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == 'DateTimeOriginal':
                            # EXIF 时间格式：'YYYY:MM:DD HH:MM:SS'
                            return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
        except Exception as e:
            self._logger.debug(f"Failed to extract EXIF time: {e}")
        return None
    
    def _extract_ocr_time(self, image: np.ndarray) -> list[Dict[str, Any]]:
        """OCR 识别图片中的时间信息"""
        result = self.ocr.ocr(image, cls=True)
        
        # 时间格式正则
        time_patterns = [
            r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日号]?',  # 2024-01-15, 2024 年 1 月 15 日
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',             # 2024-01-15
            r'\d{1,2}[-/月]\d{1,2}[日号]',               # 1 月 15 日
            r'\d{1,2}:\d{2}(:\d{2})?',                   # 14:30, 14:30:00
            r'\d{1,2}[点时]\d{1,2}[分]?',                # 14 点 30 分
        ]
        
        combined_pattern = '|'.join(time_patterns)
        detected_times = []
        
        if result and result[0]:
            for line in result[0]:
                if line:
                    text = line[1][0]
                    confidence = line[1][1]
                    
                    # 查找时间格式
                    matches = re.findall(combined_pattern, text)
                    for match in matches:
                        detected_times.append({
                            'text': text,
                            'time_string': match if isinstance(match, str) else match[0],
                            'confidence': confidence,
                            'position': line[0]
                        })
        
        return detected_times
    
    def _parse_time_string(self, time_str: str) -> Optional[datetime]:
        """解析时间字符串"""
        try:
            # 标准化时间格式
            time_str = time_str.replace('年', '-').replace('月', '-').replace('日', '')
            time_str = time_str.replace('号', '').replace('点', ':').replace('分', '')
            
            return date_parser.parse(time_str, fuzzy=True)
        except Exception:
            return None
    
    def _verify_time_consistency(
        self, 
        exif_time: Optional[datetime],
        ocr_times: list[Dict[str, Any]],
        described_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """验证时间一致性"""
        issues = []
        
        # 解析描述时间
        described_dt = None
        if described_time:
            try:
                described_dt = date_parser.parse(described_time, fuzzy=True)
            except Exception:
                issues.append(f"无法解析描述时间：{described_time}")
        
        # 对比 EXIF 时间和描述时间
        if exif_time and described_dt:
            time_diff = abs((exif_time - described_dt).total_seconds())
            if time_diff > 86400:  # 相差超过 1 天
                issues.append(f"EXIF 时间与描述时间相差较大：{time_diff/3600:.1f}小时")
        
        # 对比 OCR 时间和 EXIF 时间
        ocr_parsed = []
        for ocr in ocr_times:
            parsed = self._parse_time_string(ocr['time_string'])
            if parsed:
                ocr_parsed.append({**ocr, 'parsed': parsed})
        
        if exif_time and ocr_parsed:
            for ocr in ocr_parsed:
                # 只对比日期部分
                if exif_time.date() != ocr['parsed'].date():
                    issues.append(f"OCR 时间 ({ocr['time_string']}) 与 EXIF 日期不一致")
        
        return {
            'is_consistent': len(issues) == 0,
            'issues': issues,
            'exif_time': str(exif_time) if exif_time else None,
            'described_time': str(described_dt) if described_dt else None,
            'ocr_times': [o['time_string'] for o in ocr_times]
        }
    
    def _detect(self, image_info) -> DetectionResult:
        """执行时间校验"""
        image_path = image_info.path if hasattr(image_info, 'path') else str(image_info)
        image = cv2.imread(image_path)
        
        # 提取 EXIF 时间
        exif_time = self._extract_exif_time(image_path)
        
        # OCR 识别时间
        ocr_times = []
        if image is not None and self.ocr:
            ocr_times = self._extract_ocr_time(image)
        
        # 获取描述时间（如果有）
        described_time = getattr(image_info, 'described_time', None)
        
        # 验证一致性
        verification = self._verify_time_consistency(exif_time, ocr_times, described_time)
        
        is_anomaly = not verification['is_consistent']
        confidence = 0.9 if not is_anomaly else 0.7
        
        description = "时间校验通过" if not is_anomaly else f"时间不一致：{'; '.join(verification['issues'])}"
        
        return DetectionResult(
            detector_name=self._name,
            detection_type=self._detection_type,
            is_anomaly=is_anomaly,
            confidence=confidence,
            description=description,
            details=verification
        )
```

#### 依赖配置

```txt
Pillow>=10.0.0
python-dateutil>=2.8.0
paddleocr>=2.7.0
```

---

### 1.3 地点校验

**功能**: 验证图片地点与描述是否一致（如门店名称、地理位置）

**技术方案**:

| 方案 | 技术 | 适用场景 | 难度 |
|------|------|----------|------|
| OCR+ 关键词匹配 | PaddleOCR + NLP | 门店名、地名识别 | 中等 |
| 地标识别 | CLIP/ResNet + 特征库 | 知名地标 | 较高 |
| GPS 校验 | EXIF GPS 读取 | 有 GPS 信息的图片 | 简单 |

**推荐路线**: GPS 校验 + OCR 地名识别

#### 实现代码

```python
# detectors/basic/location_validator.py
"""
地点校验器
- EXIF GPS 提取 + 距离计算
- OCR 识别地名 + 关键词匹配
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.distance import geodesic
from typing import Optional, Tuple, List, Dict, Any
import cv2
import re
from paddleocr import PaddleOCR
from ai_check.core import DetectorBase, DetectionResult, DetectionType


class LocationValidator(DetectorBase):
    """地点校验器"""
    
    def __init__(self, name="location_validator", config=None):
        super().__init__(name, DetectionType.BASIC, config)
        self.ocr = None
        self.target_location: Optional[Tuple[float, float]] = None
        self.target_place_names: List[str] = []
        self.gps_tolerance_km = 1.0  # GPS 容差（公里）
    
    def _initialize(self) -> bool:
        """初始化 OCR 引擎"""
        try:
            self.ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
            return True
        except Exception as e:
            self._logger.error(f"Failed to initialize PaddleOCR: {e}")
            return False
    
    def set_target_location(self, latitude: float, longitude: float, tolerance_km: float = 1.0):
        """设置目标地理位置"""
        self.target_location = (latitude, longitude)
        self.gps_tolerance_km = tolerance_km
    
    def set_target_place_names(self, place_names: List[str]):
        """设置目标地点名称（如门店名）"""
        self.target_place_names = place_names
    
    def _extract_gps(self, image_path: str) -> Optional[Tuple[float, float]]:
        """从 EXIF 提取 GPS 坐标"""
        try:
            with Image.open(image_path) as img:
                exif = img._getexif()
                if not exif:
                    return None
                
                # 查找 GPS 信息
                gps_info = None
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'GPSInfo':
                        gps_info = value
                        break
                
                if not gps_info:
                    return None
                
                # 解析 GPS 坐标
                def convert_to_degrees(value):
                    d = float(value[0][0]) / float(value[0][1])
                    m = float(value[1][0]) / float(value[1][1])
                    s = float(value[2][0]) / float(value[2][1])
                    return d + (m / 60.0) + (s / 3600.0)
                
                lat = convert_to_degrees(gps_info[2])
                if gps_info[1] == 'S':
                    lat = -lat
                
                lon = convert_to_degrees(gps_info[4])
                if gps_info[3] == 'W':
                    lon = -lon
                
                return (lat, lon)
        except Exception as e:
            self._logger.debug(f"Failed to extract GPS: {e}")
            return None
    
    def _verify_gps(self, image_path: str) -> Dict[str, Any]:
        """验证 GPS 位置"""
        if not self.target_location:
            return {'match': None, 'reason': '未设置目标位置'}
        
        gps = self._extract_gps(image_path)
        if not gps:
            return {'match': None, 'reason': '无 GPS 数据'}
        
        distance = geodesic(gps, self.target_location).kilometers
        is_match = distance <= self.gps_tolerance_km
        
        return {
            'match': is_match,
            'distance_km': distance,
            'tolerance_km': self.gps_tolerance_km,
            'image_gps': gps,
            'target_gps': self.target_location
        }
    
    def _extract_place_names(self, image: np.ndarray) -> List[str]:
        """OCR 识别地点名称"""
        result = self.ocr.ocr(image, cls=True)
        
        place_keywords = [
            '店', '铺', '商场', '广场', '中心',
            '市', '城', '街', '路', '道',
            '大厦', '写字楼', '酒店', '餐厅'
        ]
        
        detected_places = []
        
        if result and result[0]:
            for line in result[0]:
                if line:
                    text = line[1][0]
                    # 检查是否包含地点关键词
                    for keyword in place_keywords:
                        if keyword in text:
                            detected_places.append(text)
                            break
        
        return detected_places
    
    def _verify_place_names(self, detected_places: List[str]) -> Dict[str, Any]:
        """验证地点名称匹配"""
        if not self.target_place_names:
            return {'match': None, 'reason': '未设置目标地点名称'}
        
        matched = []
        for target in self.target_place_names:
            for detected in detected_places:
                # 简单包含匹配
                if target in detected or detected in target:
                    matched.append({
                        'target': target,
                        'detected': detected
                    })
        
        return {
            'match': len(matched) > 0,
            'matched_pairs': matched,
            'detected_places': detected_places,
            'target_places': self.target_place_names
        }
    
    def _detect(self, image_info) -> DetectionResult:
        """执行地点校验"""
        image_path = image_info.path if hasattr(image_info, 'path') else str(image_info)
        image = cv2.imread(image_path)
        
        results = {}
        is_anomaly = False
        issues = []
        
        # GPS 验证
        gps_result = self._verify_gps(image_path)
        results['gps'] = gps_result
        if gps_result.get('match') is False:
            is_anomaly = True
            issues.append(f"GPS 位置偏差 {gps_result.get('distance_km', 0):.2f}km")
        
        # 地点名称验证
        if image is not None and self.ocr:
            detected_places = self._extract_place_names(image)
            place_result = self._verify_place_names(detected_places)
            results['place_name'] = place_result
            
            if place_result.get('match') is False:
                is_anomaly = True
                issues.append("未检测到目标地点名称")
        
        confidence = 0.9 if not is_anomaly else 0.7
        description = "地点校验通过" if not is_anomaly else f"地点不一致：{'; '.join(issues)}"
        
        return DetectionResult(
            detector_name=self._name,
            detection_type=self._detection_type,
            is_anomaly=is_anomaly,
            confidence=confidence,
            description=description,
            details=results
        )
```

#### 依赖配置

```txt
geopy>=2.4.0
Pillow>=10.0.0
paddleocr>=2.7.0
```

---

### 1.4 图片质量校验

**功能**: 检测图片清晰度、过曝、欠曝等质量问题

**技术方案**:

| 检测项 | 算法 | 阈值参考 |
|--------|------|----------|
| 清晰度 | Laplacian 方差 | < 100 为模糊 |
| 过曝检测 | 直方图分析 | >250 像素占比>30% |
| 欠曝检测 | 直方图分析 | <10 像素占比>50% |
| 噪声水平 | 信噪比计算 | SNR < 20dB 为差 |

#### 实现代码

```python
# detectors/basic/quality_checker.py
"""
图片质量校验器
- 清晰度检测（Laplacian 方差）
- 过曝/欠曝检测（直方图分析）
- 噪声水平评估
"""

import cv2
import numpy as np
from typing import Dict, Any
from ai_check.core import DetectorBase, DetectionResult, DetectionType


class QualityChecker(DetectorBase):
    """图片质量校验器"""
    
    def __init__(self, name="quality_checker", config=None):
        super().__init__(name, DetectionType.BASIC, config)
        # 可配置的阈值
        self.blur_threshold = 100  # 清晰度阈值
        self.overexposed_ratio_threshold = 0.3  # 过曝比例阈值
        self.underexposed_ratio_threshold = 0.5  # 欠曝比例阈值
        self.snr_threshold = 20  # 信噪比阈值 (dB)
    
    def _check_blur(self, image: np.ndarray) -> Dict[str, Any]:
        """拉普拉斯方差检测模糊"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        is_blurry = variance < self.blur_threshold
        
        # 质量等级
        if variance < 50:
            quality = 'very_poor'
        elif variance < 100:
            quality = 'poor'
        elif variance < 200:
            quality = 'fair'
        elif variance < 500:
            quality = 'good'
        else:
            quality = 'excellent'
        
        return {
            'is_blurry': is_blurry,
            'sharpness_score': variance,
            'threshold': self.blur_threshold,
            'quality_level': quality
        }
    
    def _check_exposure(self, image: np.ndarray) -> Dict[str, Any]:
        """直方图分析检测过曝/欠曝"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 计算过曝和欠曝比例
        overexposed_ratio = np.sum(gray > 250) / gray.size
        underexposed_ratio = np.sum(gray < 10) / gray.size
        
        is_overexposed = overexposed_ratio > self.overexposed_ratio_threshold
        is_underexposed = underexposed_ratio > self.underexposed_ratio_threshold
        
        # 计算平均亮度
        mean_brightness = np.mean(gray)
        
        # 质量等级
        if is_overexposed:
            quality = 'overexposed'
        elif is_underexposed:
            quality = 'underexposed'
        elif 80 < mean_brightness < 180:
            quality = 'good'
        else:
            quality = 'fair'
        
        return {
            'is_overexposed': is_overexposed,
            'is_underexposed': is_underexposed,
            'overexposed_ratio': overexposed_ratio,
            'underexposed_ratio': underexposed_ratio,
            'mean_brightness': mean_brightness,
            'quality_level': quality
        }
    
    def _check_noise(self, image: np.ndarray) -> Dict[str, Any]:
        """噪声水平评估"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(float)
        
        # 高通滤波提取噪声
        kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        noise = cv2.filter2D(gray, -1, kernel)
        
        # 计算信噪比
        signal = gray - noise
        snr = 10 * np.log10(np.var(signal) / np.var(noise)) if np.var(noise) > 0 else float('inf')
        
        is_noisy = snr < self.snr_threshold
        
        # 质量等级
        if snr < 15:
            quality = 'very_poor'
        elif snr < 20:
            quality = 'poor'
        elif snr < 30:
            quality = 'fair'
        else:
            quality = 'good'
        
        return {
            'is_noisy': is_noisy,
            'snr_db': snr,
            'threshold': self.snr_threshold,
            'quality_level': quality
        }
    
    def _check_all(self, image: np.ndarray) -> Dict[str, Any]:
        """综合质量评估"""
        blur_result = self._check_blur(image)
        exposure_result = self._check_exposure(image)
        noise_result = self._check_noise(image)
        
        # 计算综合得分
        issues = []
        if blur_result['is_blurry']:
            issues.append('blurry')
        if exposure_result['is_overexposed']:
            issues.append('overexposed')
        if exposure_result['is_underexposed']:
            issues.append('underexposed')
        if noise_result['is_noisy']:
            issues.append('noisy')
        
        # 质量等级映射
        quality_scores = {
            'excellent': 5,
            'good': 4,
            'fair': 3,
            'poor': 2,
            'very_poor': 1
        }
        
        avg_score = (
            quality_scores.get(blur_result['quality_level'], 3) +
            quality_scores.get(exposure_result['quality_level'], 3) +
            quality_scores.get(noise_result['quality_level'], 3)
        ) / 3
        
        overall_quality = 'excellent' if avg_score >= 4.5 else \
                         'good' if avg_score >= 3.5 else \
                         'fair' if avg_score >= 2.5 else \
                         'poor'
        
        return {
            'blur': blur_result,
            'exposure': exposure_result,
            'noise': noise_result,
            'issues': issues,
            'overall_quality': overall_quality,
            'quality_score': avg_score / 5.0,
            'passed': len(issues) == 0
        }
    
    def _detect(self, image_info) -> DetectionResult:
        """执行质量校验"""
        image_path = image_info.path if hasattr(image_info, 'path') else str(image_info)
        image = cv2.imread(image_path)
        
        if image is None:
            return DetectionResult(
                detector_name=self._name,
                detection_type=self._detection_type,
                is_anomaly=True,
                confidence=1.0,
                description="无法加载图片"
            )
        
        result = self._check_all(image)
        
        is_anomaly = not result['passed']
        confidence = result['quality_score']
        
        if is_anomaly:
            description = f"质量问题：{', '.join(result['issues'])}"
        else:
            description = f"质量良好 ({result['overall_quality']})"
        
        return DetectionResult(
            detector_name=self._name,
            detection_type=self._detection_type,
            is_anomaly=is_anomaly,
            confidence=confidence,
            description=description,
            details=result
        )
```

#### 依赖配置

```txt
opencv-python>=4.8.0
numpy>=1.24.0
```

---

## 二、内容校验模块

### 2.1 物体识别校验

**功能**: 识别图片中的物体，验证是否与描述相符

**技术方案**:

| 方案 | 模型 | 优点 | 缺点 | 推荐度 |
|------|------|------|------|--------|
| CLIP | CLIP ViT-B/32 | 零样本分类，支持文本对比 | 速度较慢 | ⭐⭐⭐⭐⭐ |
| YOLOv8 | YOLOv8n | 检测速度快，可识别多物体 | 需要标注数据 | ⭐⭐⭐⭐ |
| ResNet50 | ImageNet 预训练 | 成熟稳定 | 只能识别 1000 类 | ⭐⭐⭐ |

**推荐路线**: CLIP 零样本物体验证

#### 实现代码

```python
# detectors/content/object_validator.py
"""
物体识别校验器
- 使用 CLIP 进行零样本物体识别
- 验证图片内容是否与描述相符
"""

import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from typing import List, Dict, Any
from ai_check.core import DetectorBase, DetectionResult, DetectionType


class ObjectValidator(DetectorBase):
    """物体识别校验器"""
    
    def __init__(self, name="object_validator", config=None):
        super().__init__(name, DetectionType.CONTENT, config)
        self.model = None
        self.processor = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    def _initialize(self) -> bool:
        """加载 CLIP 模型"""
        try:
            self.model = CLIPModel.from_pretrained(
                "openai/clip-vit-base-patch32"
            ).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(
                "openai/clip-vit-base-patch32"
            )
            self.model.eval()
            return True
        except Exception as e:
            self._logger.error(f"Failed to load CLIP model: {e}")
            return False
    
    def _verify_with_clip(
        self, 
        image: Image.Image, 
        description: str
    ) -> Dict[str, Any]:
        """使用 CLIP 验证图片与描述匹配度"""
        # 构建提示
        prompts = [
            f"a photo of {description}",
            f"a picture containing {description}",
            f"an image with {description}"
        ]
        
        inputs = self.processor(
            text=prompts,
            images=image,
            return_tensors="pt",
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # 获取图片 - 文本相似度
            similarity = outputs.logits_per_image.softmax(dim=1)[0]
            max_similarity = similarity.max().item()
            avg_similarity = similarity.mean().item()
        
        return {
            'match': max_similarity > 0.5,
            'max_similarity': max_similarity,
            'avg_similarity': avg_similarity,
            'prompts': prompts
        }
    
    def _detect(self, image_info) -> DetectionResult:
        """执行物体识别校验"""
        image_path = image_info.path if hasattr(image_info, 'path') else str(image_info)
        description = getattr(image_info, 'description', None)
        
        if not description:
            return DetectionResult(
                detector_name=self._name,
                detection_type=self._detection_type,
                is_anomaly=False,
                confidence=0.0,
                description="缺少描述信息，无法校验"
            )
        
        try:
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            return DetectionResult(
                detector_name=self._name,
                detection_type=self._detection_type,
                is_anomaly=True,
                confidence=1.0,
                description=f"无法加载图片：{e}"
            )
        
        result = self._verify_with_clip(image, description)
        
        is_anomaly = not result['match']
        confidence = result['max_similarity']
        
        if is_anomaly:
            description_text = f"图片内容与描述不符 (相似度：{confidence:.2%})"
        else:
            description_text = f"图片内容与描述相符 (相似度：{confidence:.2%})"
        
        return DetectionResult(
            detector_name=self._name,
            detection_type=self._detection_type,
            is_anomaly=is_anomaly,
            confidence=confidence,
            description=description_text,
            details=result
        )
```

#### 依赖配置

```txt
torch>=2.0.0
transformers>=4.30.0
```

---

### 2.2 文字识别校验

**功能**: OCR 识别图片文字，验证是否与描述相符

**技术方案**:

| 方案 | 技术 | 中文支持 | 速度 | 推荐度 |
|------|------|----------|------|--------|
| PaddleOCR | PP-OCRv4 | 优秀 | 快 | ⭐⭐⭐⭐⭐ |
| Tesseract | LSTM | 一般 | 慢 | ⭐⭐⭐ |
| EasyOCR | CRNN | 良好 | 中等 | ⭐⭐⭐⭐ |

**推荐路线**: PaddleOCR

#### 实现代码

```python
# detectors/content/text_validator.py
"""
文字识别校验器
- 使用 PaddleOCR 识别图片文字
- 验证识别文字是否与描述相符
"""

from paddleocr import PaddleOCR
from difflib import SequenceMatcher
from typing import List, Dict, Any
import cv2
from ai_check.core import DetectorBase, DetectionResult, DetectionType


class TextValidator(DetectorBase):
    """文字识别校验器"""
    
    def __init__(self, name="text_validator", config=None):
        super().__init__(name, DetectionType.CONTENT, config)
        self.ocr = None
        self.expected_texts: List[str] = []
        self.similarity_threshold = 0.8
    
    def _initialize(self) -> bool:
        """初始化 OCR 引擎"""
        try:
            self.ocr = PaddleOCR(
                use_angle_cls=True, 
                lang='ch',
                show_log=False
            )
            return True
        except Exception as e:
            self._logger.error(f"Failed to initialize PaddleOCR: {e}")
            return False
    
    def set_expected_texts(self, texts: List[str]):
        """设置期望的文字内容"""
        self.expected_texts = texts
    
    def _compute_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _verify_texts(
        self, 
        detected_texts: List[str], 
        expected_texts: List[str]
    ) -> Dict[str, Any]:
        """验证检测文字与期望文字匹配度"""
        results = []
        
        for expected in expected_texts:
            best_match = None
            best_similarity = 0
            
            for detected in detected_texts:
                sim = self._compute_similarity(detected, expected)
                if sim > best_similarity:
                    best_similarity = sim
                    best_match = detected
            
            results.append({
                'expected': expected,
                'best_match': best_match,
                'similarity': best_similarity,
                'match': best_similarity >= self.similarity_threshold
            })
        
        all_matched = all(r['match'] for r in results)
        
        return {
            'all_matched': all_matched,
            'results': results,
            'detected_texts': detected_texts,
            'expected_texts': expected_texts
        }
    
    def _detect(self, image_info) -> DetectionResult:
        """执行文字识别校验"""
        image_path = image_info.path if hasattr(image_info, 'path') else str(image_info)
        image = cv2.imread(image_path)
        
        if image is None:
            return DetectionResult(
                detector_name=self._name,
                detection_type=self._detection_type,
                is_anomaly=True,
                confidence=1.0,
                description="无法加载图片"
            )
        
        # OCR 识别
        result = self.ocr.ocr(image, cls=True)
        detected_texts = []
        
        if result and result[0]:
            for line in result[0]:
                if line:
                    detected_texts.append(line[1][0])
        
        # 获取期望文字
        expected_texts = getattr(image_info, 'expected_texts', self.expected_texts)
        
        if not expected_texts:
            # 仅返回识别结果，不做比对
            return DetectionResult(
                detector_name=self._name,
                detection_type=self._detection_type,
                is_anomaly=False,
                confidence=1.0,
                description=f"识别到 {len(detected_texts)} 段文字",
                details={'detected_texts': detected_texts}
            )
        
        # 验证匹配
        verification = self._verify_texts(detected_texts, expected_texts)
        
        is_anomaly = not verification['all_matched']
        confidence = max([r['similarity'] for r in verification['results']], default=0)
        
        if is_anomaly:
            unmatched = [r['expected'] for r in verification['results'] if not r['match']]
            description = f"未找到期望文字：{', '.join(unmatched)}"
        else:
            description = "文字内容校验通过"
        
        return DetectionResult(
            detector_name=self._name,
            detection_type=self._detection_type,
            is_anomaly=is_anomaly,
            confidence=confidence,
            description=description,
            details=verification
        )
```

#### 依赖配置

```txt
paddlepaddle>=2.5.0
paddleocr>=2.7.0
```

---

## 三、高级校验模块

### 3.1 AI 生成图片检测

**功能**: 识别图片是否由 AI 生成（Midjourney、Stable Diffusion 等）

**技术方案**:

| 方案 | 模型/方法 | 准确率 | 难度 | 推荐度 |
|------|-----------|--------|------|--------|
| 频域分析 | DCT + 分类器 | ~80% | 中等 | ⭐⭐⭐⭐ |
| 噪声分析 | SRM + CNN | ~85% | 较高 | ⭐⭐⭐⭐ |
| 预训练模型 | UnivFD | ~90% | 低 | ⭐⭐⭐⭐⭐ |
| 多特征融合 | 频域 + 噪声 + 纹理 | ~92% | 高 | ⭐⭐⭐⭐ |

**推荐路线**: UnivFD 预训练模型

#### 实现代码

```python
# detectors/advanced/ai_generator_detector.py
"""
AI 生成图片检测器
- 使用 UnivFD 预训练模型检测 AI 生成图片
- 支持频域分析作为补充
"""

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np
from typing import Dict, Any
from ai_check.core import DetectorBase, DetectionResult, DetectionType


class AIGeneratedDetector(DetectorBase):
    """AI 生成图片检测器"""
    
    def __init__(self, name="ai_generator_detector", config=None):
        super().__init__(name, DetectionType.ADVANCED, config)
        self.model = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.threshold = 0.5
        
        # 图像预处理
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def _initialize(self) -> bool:
        """加载 UnivFD 模型"""
        try:
            # 使用 torch.hub 加载 Facebook 的 UnivFD 模型
            self.model = torch.hub.load(
                'facebookresearch/univfd', 
                'univfd_resnet50',
                pretrained=True
            )
            self.model = self.model.to(self.device)
            self.model.eval()
            return True
        except Exception as e:
            self._logger.error(f"Failed to load UnivFD model: {e}")
            return False
    
    def _detect_with_univfd(self, image: Image.Image) -> Dict[str, Any]:
        """使用 UnivFD 检测 AI 生成图片"""
        img_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(img_tensor)
            # 输出 [real_prob, fake_prob]
            probs = F.softmax(output, dim=1)[0]
            ai_prob = probs[1].item()
        
        return {
            'is_ai_generated': ai_prob > self.threshold,
            'ai_probability': ai_prob,
            'real_probability': probs[0].item(),
            'confidence': max(ai_prob, probs[0].item()),
            'method': 'univfd'
        }
    
    def _frequency_analysis(self, image: Image.Image) -> Dict[str, Any]:
        """频域分析作为补充检测"""
        # 转换为灰度图
        img_array = np.array(image.convert('L')).astype(float)
        
        # DCT 变换
        from scipy import fftpack
        dct_coeffs = fftpack.dct(fftpack.dct(img_array, axis=0), axis=1)
        
        # 计算高频分量能量占比
        h, w = dct_coeffs.shape
        high_freq = dct_coeffs[h//4:, w//4:]
        total_energy = np.sum(dct_coeffs ** 2)
        high_freq_energy = np.sum(high_freq ** 2)
        
        energy_ratio = high_freq_energy / total_energy if total_energy > 0 else 0
        
        # AI 生成图片通常高频分量较少
        is_suspicious = energy_ratio < 0.1
        
        return {
            'is_suspicious': is_suspicious,
            'high_freq_energy_ratio': energy_ratio,
            'method': 'frequency_analysis'
        }
    
    def _detect(self, image_info) -> DetectionResult:
        """执行 AI 生成检测"""
        image_path = image_info.path if hasattr(image_info, 'path') else str(image_info)
        
        try:
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            return DetectionResult(
                detector_name=self._name,
                detection_type=self._detection_type,
                is_anomaly=True,
                confidence=1.0,
                description=f"无法加载图片：{e}"
            )
        
        # UnivFD 检测
        univfd_result = self._detect_with_univfd(image)
        
        # 频域分析（可选）
        freq_result = self._frequency_analysis(image)
        
        # 综合判断
        is_ai_generated = univfd_result['is_ai_generated']
        confidence = univfd_result['ai_probability']
        
        # 如果频域分析也可疑，提高置信度
        if freq_result['is_suspicious'] and is_ai_generated:
            confidence = min(confidence + 0.1, 1.0)
        
        description = (
            f"疑似 AI 生成图片 (置信度：{confidence:.2%})" if is_ai_generated
            else f"真实图片 (置信度：{1-confidence:.2%})"
        )
        
        return DetectionResult(
            detector_name=self._name,
            detection_type=self._detection_type,
            is_anomaly=is_ai_generated,
            confidence=confidence,
            description=description,
            details={
                'univfd': univfd_result,
                'frequency_analysis': freq_result
            }
        )
```

#### 依赖配置

```txt
torch>=2.0.0
torchvision>=0.15.0
scipy>=1.10.0
```

---

### 3.2 PS 伪造检测

**功能**: 检测图片是否有 PS 痕迹、不一致区域

**技术方案**:

| 检测方法 | 算法 | 检测内容 | 难度 | 推荐度 |
|----------|------|----------|------|--------|
| ELA | Error Level Analysis | 压缩不一致区域 | 简单 | ⭐⭐⭐⭐ |
| 噪声一致性 | 噪声方差分析 | 拼接区域噪声差异 | 中等 | ⭐⭐⭐⭐ |
| 光照分析 | 光源方向估计 | 光照不一致 | 较高 | ⭐⭐⭐ |
| 元数据分析 | EXIF/编辑历史 | 编辑软件痕迹 | 简单 | ⭐⭐⭐⭐ |

**推荐路线**: ELA 分析 + 噪声一致性

#### 实现代码

```python
# detectors/advanced/ps_forgery_detector.py
"""
PS 伪造检测器
- ELA（Error Level Analysis）分析
- 噪声一致性分析
- 元数据分析
"""

import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
from typing import Dict, Any, List, Tuple
from ai_check.core import DetectorBase, DetectionResult, DetectionType


class PSForgeryDetector(DetectorBase):
    """PS 伪造检测器"""
    
    def __init__(self, name="ps_forgery_detector", config=None):
        super().__init__(name, DetectionType.ADVANCED, config)
        self.jpeg_quality = 90
        self.ela_threshold = 30
        self.noise_threshold = 5
    
    def _ela_analysis(self, image: np.ndarray) -> Dict[str, Any]:
        """Error Level Analysis"""
        # 重新压缩
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
        _, encoded = cv2.imencode('.jpg', image, encode_param)
        decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        
        # 计算差异
        diff = cv2.absdiff(image, decoded)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # 归一化
        diff_normalized = cv2.normalize(diff_gray, None, 0, 255, cv2.NORM_MINMAX)
        
        # 二值化查找高差异区域
        _, binary = cv2.threshold(diff_normalized, self.ela_threshold, 255, cv2.THRESH_BINARY)
        
        # 形态学操作
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        tampered_regions = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 10 and h > 10:  # 过滤小区域
                tampered_regions.append({
                    'position': (x, y, w, h),
                    'area': w * h,
                    'confidence': min(1.0, (w * h) / 1000)
                })
        
        # 按面积排序
        tampered_regions.sort(key=lambda x: x['area'], reverse=True)
        
        has_tampering = len(tampered_regions) > 0
        confidence = max([r['confidence'] for r in tampered_regions], default=0)
        
        return {
            'has_tampering': has_tampering,
            'tampered_regions': tampered_regions[:5],  # 只保留前 5 个
            'confidence': confidence,
            'method': 'ela'
        }
    
    def _noise_consistency_analysis(self, image: np.ndarray) -> Dict[str, Any]:
        """噪声一致性分析"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(float)
        
        # 高通滤波提取噪声
        kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        noise = cv2.filter2D(gray, -1, kernel)
        
        # 分块分析
        h, w = noise.shape
        block_size = 64
        block_stds = []
        block_positions = []
        
        for y in range(0, h - block_size, block_size):
            for x in range(0, w - block_size, block_size):
                block = noise[y:y+block_size, x:x+block_size]
                std = np.std(block)
                block_stds.append(std)
                block_positions.append((x, y))
        
        # 计算噪声标准差的不一致性
        inconsistency = np.std(block_stds)
        mean_noise = np.mean(block_stds)
        
        # 找出异常块
        anomaly_blocks = []
        for i, (std, pos) in enumerate(zip(block_stds, block_positions)):
            if abs(std - mean_noise) > 2 * inconsistency:
                anomaly_blocks.append({
                    'position': pos,
                    'std': std,
                    'deviation': abs(std - mean_noise)
                })
        
        has_inconsistency = inconsistency > self.noise_threshold
        
        return {
            'has_inconsistency': has_inconsistency,
            'inconsistency_score': inconsistency,
            'mean_noise_level': mean_noise,
            'anomaly_blocks': anomaly_blocks[:5],
            'method': 'noise_consistency'
        }
    
    def _analyze_metadata(self, image_path: str) -> Dict[str, Any]:
        """元数据分析"""
        try:
            with Image.open(image_path) as img:
                exif = img._getexif()
                
                if not exif:
                    return {'has_metadata': False, 'suspicious': False}
                
                metadata = {}
                suspicious_signs = []
                
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    metadata[tag] = str(value) if not isinstance(value, (int, float)) else value
                
                # 检查可疑迹象
                # 1. 编辑软件痕迹
                if 'Software' in metadata:
                    software = str(metadata['Software']).lower()
                    if any(ps in software for ps in ['photoshop', 'gimp', 'affinity']):
                        suspicious_signs.append(f"检测到编辑软件：{metadata['Software']}")
                
                # 2. 修改历史
                if 'ModifyDate' in metadata and 'CreateDate' in metadata:
                    if metadata['ModifyDate'] != metadata['CreateDate']:
                        suspicious_signs.append("图片被修改过")
                
                return {
                    'has_metadata': True,
                    'metadata': metadata,
                    'suspicious': len(suspicious_signs) > 0,
                    'suspicious_signs': suspicious_signs
                }
        except Exception as e:
            return {'has_metadata': False, 'suspicious': False, 'error': str(e)}
    
    def _combine_results(
        self, 
        ela_result: Dict, 
        noise_result: Dict, 
        metadata_result: Dict
    ) -> Dict[str, Any]:
        """综合多个检测结果"""
        scores = []
        methods = []
        
        # ELA 结果
        if ela_result['has_tampering']:
            scores.append(ela_result['confidence'])
            methods.append('ela')
        
        # 噪声分析结果
        if noise_result['has_inconsistency']:
            noise_confidence = min(1.0, noise_result['inconsistency_score'] / 10)
            scores.append(noise_confidence)
            methods.append('noise')
        
        # 元数据结果
        if metadata_result.get('suspicious'):
            scores.append(0.7)  # 元数据可疑的置信度
            methods.append('metadata')
        
        is_tampered = len(scores) >= 2 or (len(scores) == 1 and scores[0] > 0.8)
        confidence = np.mean(scores) if scores else 0
        
        return {
            'is_tampered': is_tampered,
            'confidence': confidence,
            'methods_triggered': methods,
            'ela': ela_result,
            'noise': noise_result,
            'metadata': metadata_result
        }
    
    def _detect(self, image_info) -> DetectionResult:
        """执行 PS 伪造检测"""
        image_path = image_info.path if hasattr(image_info, 'path') else str(image_info)
        image = cv2.imread(image_path)
        
        if image is None:
            return DetectionResult(
                detector_name=self._name,
                detection_type=self._detection_type,
                is_anomaly=True,
                confidence=1.0,
                description="无法加载图片"
            )
        
        # ELA 分析
        ela_result = self._ela_analysis(image)
        
        # 噪声一致性分析
        noise_result = self._noise_consistency_analysis(image)
        
        # 元数据分析
        metadata_result = self._analyze_metadata(image_path)
        
        # 综合判断
        combined = self._combine_results(ela_result, noise_result, metadata_result)
        
        is_anomaly = combined['is_tampered']
        confidence = combined['confidence']
        
        if is_anomaly:
            methods = combined['methods_triggered']
            description = f"检测到 PS 伪造痕迹 ({', '.join(methods)})"
        else:
            description = "未检测到明显 PS 痕迹"
        
        return DetectionResult(
            detector_name=self._name,
            detection_type=self._detection_type,
            is_anomaly=is_anomaly,
            confidence=confidence,
            description=description,
            details=combined
        )
```

#### 依赖配置

```txt
opencv-python>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0
```

---

### 3.3 重复图片检测

**功能**: 检测图片是否与数据库中图片重复或相似

**技术方案**:

| 层级 | 方法 | 用途 | 速度 | 推荐度 |
|------|------|------|------|--------|
| 精确重复 | MD5/SHA1 | 完全相同图片 | 极快 | ⭐⭐⭐⭐⭐ |
| 感知哈希 | pHash/dHash/aHash | 轻微修改图片 | 快 | ⭐⭐⭐⭐⭐ |
| 局部特征 | SIFT/ORB | 旋转、缩放图片 | 中等 | ⭐⭐⭐⭐ |
| 深度特征 | CLIP/ResNet + FAISS | 语义相似图片 | 较慢 | ⭐⭐⭐⭐⭐ |

**推荐路线**: MD5 + pHash + FAISS 深度特征（分层检测）

#### 实现代码

```python
# detectors/advanced/duplicate_detector.py
"""
重复图片检测器
- MD5 精确重复检测
- 感知哈希 (pHash) 相似检测
- FAISS 深度特征检索（大规模）
"""

import hashlib
import imagehash
from PIL import Image
import numpy as np
from typing import Dict, Any, List, Optional
from ai_check.core import DetectorBase, DetectionResult, DetectionType


class DuplicateDetector(DetectorBase):
    """重复图片检测器"""
    
    def __init__(self, name="duplicate_detector", config=None):
        super().__init__(name, DetectionType.ADVANCED, config)
        self.hash_db: Dict[str, str] = {}  # hash -> image_id
        self.similarity_threshold = 5  # 汉明距离阈值
        self.use_faiss = False
        self.faiss_index = None
        self.feature_dim = 512
    
    def _initialize(self) -> bool:
        """初始化"""
        try:
            # 可选：初始化 FAISS 索引
            # self._init_faiss()
            return True
        except Exception as e:
            self._logger.error(f"Failed to initialize: {e}")
            return False
    
    def _compute_md5(self, image_path: str) -> str:
        """计算 MD5 哈希"""
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _compute_phash(self, image_path: str) -> str:
        """计算感知哈希"""
        with Image.open(image_path).convert('RGB') as img:
            return str(imagehash.phash(img))
    
    def _compute_dhash(self, image_path: str) -> str:
        """计算差异哈希"""
        with Image.open(image_path).convert('RGB') as img:
            return str(imagehash.dhash(img))
    
    def _compute_ahash(self, image_path: str) -> str:
        """计算平均哈希"""
        with Image.open(image_path).convert('RGB') as img:
            return str(imagehash.average_hash(img))
    
    def _hex_to_hash(self, hex_str: str) -> int:
        """十六进制字符串转整数"""
        return int(hex_str, 16)
    
    def _hamming_distance(self, hash1: str, hash2: str) -> int:
        """计算汉明距离"""
        h1 = self._hex_to_hash(hash1)
        h2 = self._hex_to_hash(hash2)
        xor = h1 ^ h2
        return bin(xor).count('1')
    
    def add_to_database(self, image_id: str, image_path: str):
        """添加图片到数据库"""
        phash = self._compute_phash(image_path)
        self.hash_db[phash] = image_id
    
    def _find_exact_duplicate(self, md5_hash: str) -> Dict[str, Any]:
        """查找精确重复"""
        # 这里应该查询数据库
        # 简化示例：
        for stored_md5, image_id in getattr(self, 'md5_db', {}).items():
            if stored_md5 == md5_hash:
                return {
                    'is_duplicate': True,
                    'duplicate_of': image_id,
                    'type': 'exact',
                    'confidence': 1.0
                }
        return {'is_duplicate': False}
    
    def _find_similar_by_phash(
        self, 
        phash: str, 
        threshold: int = 5
    ) -> Dict[str, Any]:
        """通过 pHash 查找相似图片"""
        for stored_hash, image_id in self.hash_db.items():
            distance = self._hamming_distance(phash, stored_hash)
            if distance <= threshold:
                similarity = 1 - distance / 64  # pHash 通常 64 位
                return {
                    'is_duplicate': True,
                    'duplicate_of': image_id,
                    'type': 'similar',
                    'hamming_distance': distance,
                    'similarity': similarity,
                    'confidence': similarity
                }
        return {'is_duplicate': False}
    
    def _detect(self, image_info) -> DetectionResult:
        """执行重复检测"""
        image_path = image_info.path if hasattr(image_info, 'path') else str(image_info)
        
        try:
            # 计算哈希
            md5_hash = self._compute_md5(image_path)
            phash = self._compute_phash(image_path)
            
            # 1. 精确重复检测
            exact_result = self._find_exact_duplicate(md5_hash)
            if exact_result['is_duplicate']:
                return DetectionResult(
                    detector_name=self._name,
                    detection_type=self._detection_type,
                    is_anomaly=True,
                    confidence=1.0,
                    description=f"精确重复：{exact_result['duplicate_of']}",
                    details=exact_result
                )
            
            # 2. 相似图片检测
            similar_result = self._find_similar_by_phash(phash, self.similarity_threshold)
            if similar_result['is_duplicate']:
                return DetectionResult(
                    detector_name=self._name,
                    detection_type=self._detection_type,
                    is_anomaly=True,
                    confidence=similar_result['confidence'],
                    description=f"相似图片：{similar_result['duplicate_of']} (相似度：{similar_result['similarity']:.2%})",
                    details=similar_result
                )
            
            # 无重复
            return DetectionResult(
                detector_name=self._name,
                detection_type=self._detection_type,
                is_anomaly=False,
                confidence=1.0,
                description="未检测到重复",
                details={
                    'md5': md5_hash,
                    'phash': phash
                }
            )
            
        except Exception as e:
            return DetectionResult(
                detector_name=self._name,
                detection_type=self._detection_type,
                is_anomaly=False,
                confidence=0.0,
                description=f"检测失败：{e}"
            )
```

#### 依赖配置

```txt
imagehash>=4.3.0
Pillow>=10.0.0
faiss-cpu>=1.7.4  # 可选，用于大规模检索
```

---

## 四、检测器注册与使用

### 4.1 注册检测器

```python
# detectors/__init__.py
from ai_check.core import DetectorRegistry

# 基础校验
from .basic.watermark_detector import WatermarkDetector
from .basic.time_validator import TimeValidator
from .basic.location_validator import LocationValidator
from .basic.quality_checker import QualityChecker

# 内容校验
from .content.object_validator import ObjectValidator
from .content.text_validator import TextValidator

# 高级校验
from .advanced.ai_generator_detector import AIGeneratedDetector
from .advanced.ps_forgery_detector import PSForgeryDetector
from .advanced.duplicate_detector import DuplicateDetector

# 注册所有检测器
DetectorRegistry.register("watermark_detector")(WatermarkDetector)
DetectorRegistry.register("time_validator")(TimeValidator)
DetectorRegistry.register("location_validator")(LocationValidator)
DetectorRegistry.register("quality_checker")(QualityChecker)
DetectorRegistry.register("object_validator")(ObjectValidator)
DetectorRegistry.register("text_validator")(TextValidator)
DetectorRegistry.register("ai_generator_detector")(AIGeneratedDetector)
DetectorRegistry.register("ps_forgery_detector")(PSForgeryDetector)
DetectorRegistry.register("duplicate_detector")(DuplicateDetector)
```

### 4.2 使用示例

```python
# 使用示例
from ai_check.core import Pipeline, PipelineConfig, DetectorRegistry

# 创建流水线配置
config = PipelineConfig(
    enabled_detectors=[
        "quality_checker",
        "watermark_detector", 
        "time_validator",
        "ps_forgery_detector",
        "duplicate_detector"
    ],
    parallel=True,
    max_workers=4
)

# 创建流水线
pipeline = Pipeline(config)

# 添加检测器
for detector_name in config.enabled_detectors:
    detector_cls = DetectorRegistry.get_detector(detector_name)
    if detector_cls:
        pipeline.add_detector(detector_cls())

# 执行检测
from ai_check.core import ImageInfo

image_info = ImageInfo(
    path="test.jpg",
    description="合同扫描件",
    expected_time="2024-01-15",
    expected_location="北京市朝阳区"
)

results = pipeline.run([image_info])

# 处理结果
for result in results:
    print(f"{result.detector_name}: {result.description}")
    if result.is_anomaly:
        print(f"  ⚠️ 异常：{result.description}")
```

---

## 五、依赖汇总

### 完整依赖列表

```txt
# 核心依赖
PyQt6>=6.5.0
onnxruntime>=1.15.0
opencv-python>=4.8.0
Pillow>=10.0.0
numpy>=1.24.0

# OCR
paddlepaddle>=2.5.0
paddleocr>=2.7.0

# 深度学习
torch>=2.0.0
torchvision>=0.15.0
transformers>=4.30.0

# 向量检索
faiss-cpu>=1.7.4
imagehash>=4.3.0

# 工具库
scikit-learn>=1.3.0
scipy>=1.10.0
geopy>=2.4.0
python-dateutil>=2.8.0
openpyxl>=3.1.0
pyyaml>=6.0
loguru>=0.7.0
tqdm>=4.65.0
```

### 可选依赖（按需安装）

```txt
# GPU 加速
onnxruntime-gpu>=1.15.0

# 轻量 OCR 替代
rapidocr-onnxruntime>=1.0.0
```

---

## 六、性能优化建议

### 6.1 批量处理

```python
from concurrent.futures import ThreadPoolExecutor

def batch_detect(images: list, pipeline, batch_size: int = 32):
    """批量处理图片"""
    results = []
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        for i in range(0, len(images), batch_size):
            batch = images[i:i+batch_size]
            batch_results = list(executor.map(pipeline.run, batch))
            results.extend(batch_results)
    
    return results
```

### 6.2 模型缓存

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_clip_model():
    """缓存 CLIP 模型"""
    return CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
```

### 6.3 延迟加载

```python
class LazyDetector(DetectorBase):
    """延迟加载检测器"""
    
    def __init__(self):
        super().__init__()
        self._model = None
    
    @property
    def model(self):
        if self._model is None:
            self._model = self._load_model()
        return self._model
```

---

**文档版本**: v1.0
**创建时间**: 2026-05-08
