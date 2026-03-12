"""
边缘处理器 - Edge Processor
集成视频处理、骨骼提取和隐私保护的主处理单元
Main processing unit integrating video processing, skeleton extraction, and privacy protection
"""
import time
from typing import Optional, Generator
from datetime import datetime
import numpy as np

from app.schemas.core import SkeletonData, IncidentData, IncidentType, SeverityLevel, Location, VerificationStatus
from app.edge.config import CameraConfig, PrivacyConfig, ProcessingConfig
from app.edge.skeleton_extractor import SkeletonExtractor, VideoFrame
from app.edge.privacy_engine import PrivacyEngine, PrivacyViolationError
from app.edge.degraded_mode import DegradedModeHandler, DegradedModeReason, DegradedModeConfig, OperationMode


class FallEvent:
    """跌倒事件数据结构"""
    def __init__(
        self, 
        detected: bool, 
        confidence: float, 
        timestamp: datetime,
        skeleton_data: Optional[SkeletonData] = None
    ):
        self.detected = detected
        self.confidence = confidence
        self.timestamp = timestamp
        self.skeleton_data = skeleton_data


class EdgeProcessor:
    """
    边缘处理器 - 隐私优先的视频分析主处理单元
    
    核心功能：
    1. 视频流处理 - 从摄像头捕获视频帧
    2. 骨骼提取 - 提取姿态关键点
    3. 跌倒检测 - 实时检测跌倒事件
    4. 隐私保护 - 确保不存储或传输原始视频
    
    设计原则：
    - 隐私优先：原始视频永不离开设备
    - 实时处理：目标延迟<100ms
    - 降级模式：处理失败时保持隐私保护
    """
    
    def __init__(
        self, 
        camera_config: CameraConfig,
        privacy_config: PrivacyConfig,
        processing_config: Optional[ProcessingConfig] = None,
        degraded_mode_config: Optional[DegradedModeConfig] = None
    ):
        """
        初始化边缘处理器
        
        Args:
            camera_config: 摄像头配置
            privacy_config: 隐私保护配置
            processing_config: 处理配置（可选）
            degraded_mode_config: 降级模式配置（可选）
        """
        self.camera_config = camera_config
        self.privacy_config = privacy_config
        self.processing_config = processing_config or ProcessingConfig()
        
        # 初始化组件
        self.skeleton_extractor = SkeletonExtractor(config=self.processing_config)
        self.privacy_engine = PrivacyEngine(config=privacy_config)
        self.degraded_mode_handler = DegradedModeHandler(config=degraded_mode_config)
        
        # 状态跟踪
        self.is_running = False
        self.frame_count = 0
        self.fall_detection_count = 0
        
        # 跌倒检测参数
        self.fall_threshold_height_ratio = 0.3  # 身体高度下降30%
        self.previous_skeleton: Optional[SkeletonData] = None
        
        # 云连接状态
        self.cloud_connected = True
        self.last_cloud_sync_attempt: Optional[datetime] = None
    
    def process_video_stream(self, user_id: str, max_frames: Optional[int] = None) -> Generator[SkeletonData, None, None]:
        """
        处理视频流并生成骨骼数据
        
        这是主处理循环，从摄像头捕获帧，提取骨骼数据，
        并确保隐私保护。目标性能：<100ms每帧
        
        Args:
            user_id: 用户ID
            max_frames: 最大处理帧数（用于测试，None表示无限）
            
        Yields:
            SkeletonData: 匿名化的骨骼数据
        """
        self.is_running = True
        self.frame_count = 0
        
        try:
            while self.is_running:
                # 检查帧数限制
                if max_frames is not None and self.frame_count >= max_frames:
                    break
                
                # 开始性能计时
                pipeline_start = time.time()
                
                # 步骤1: 捕获视频帧
                frame = self._capture_frame()
                
                if frame is None:
                    continue
                
                # 步骤2: 提取骨骼姿态
                pose_keypoints = self.skeleton_extractor.extract_pose(frame)
                
                if len(pose_keypoints.keypoints) == 0:
                    # 未检测到人体
                    continue
                
                # 步骤3: 转换为SkeletonData
                skeleton_data = self.skeleton_extractor.anonymize_data(pose_keypoints, user_id)
                
                # 步骤4: 隐私引擎匿名化
                anonymized_data = self.privacy_engine.anonymize_skeleton_data(skeleton_data)
                
                # 步骤5: 验证隐私合规（需求1.4）
                validation = self.privacy_engine.validate_data_transmission(anonymized_data)
                if not validation.is_valid:
                    raise PrivacyViolationError(f"Privacy validation failed: {validation.violations}")
                
                # 步骤6: 立即删除原始帧（确保不存储视频）
                del frame
                
                # 计算管道延迟
                pipeline_latency = (time.time() - pipeline_start) * 1000  # 转换为毫秒
                
                # 验证性能要求（需求1.3：<100ms）
                if pipeline_latency > self.processing_config.target_latency_ms:
                    print(f"Warning: Pipeline latency {pipeline_latency:.2f}ms exceeds target {self.processing_config.target_latency_ms}ms")
                
                self.frame_count += 1
                self.previous_skeleton = anonymized_data
                
                yield anonymized_data
                
        except Exception as e:
            # 降级模式：确保隐私保护
            self._handle_processing_failure(e)
            raise
        finally:
            self.is_running = False
    
    def _capture_frame(self) -> Optional[VideoFrame]:
        """
        从摄像头捕获视频帧
        
        注意：这是一个模拟实现。实际实现会使用OpenCV或类似库
        
        Returns:
            VideoFrame或None
        """
        # 模拟帧捕获
        # 实际实现：
        # ret, frame = self.camera.read()
        # if not ret:
        #     return None
        # return VideoFrame(frame, datetime.utcnow())
        
        # 生成模拟帧数据
        frame_data = np.random.randint(
            0, 255, 
            (self.camera_config.height, self.camera_config.width, 3),
            dtype=np.uint8
        )
        
        return VideoFrame(frame_data, datetime.utcnow())
    
    def detect_falls(self, skeleton_data: SkeletonData) -> FallEvent:
        """
        基于骨骼分析检测跌倒（需求2.1）
        
        跌倒检测算法：
        1. 计算身体中心高度（臀部到头部）
        2. 与之前的高度比较
        3. 如果高度突然下降>30%，判定为跌倒
        4. 检查身体方向（水平vs垂直）
        5. 计算置信度分数
        
        算法特点：
        - 基于骨骼关键点的几何分析
        - 多重验证减少误报
        - 实时处理，低延迟
        
        Args:
            skeleton_data: 骨骼数据
            
        Returns:
            FallEvent: 跌倒检测结果
        """
        if not self.processing_config.fall_detection_enabled:
            return FallEvent(detected=False, confidence=0.0, timestamp=skeleton_data.timestamp)
        
        # 计算当前身体高度
        current_height = self._calculate_body_height(skeleton_data)
        
        if current_height is None:
            return FallEvent(detected=False, confidence=0.0, timestamp=skeleton_data.timestamp)
        
        # 如果有之前的骨骼数据，比较高度变化
        if self.previous_skeleton is not None:
            previous_height = self._calculate_body_height(self.previous_skeleton)
            
            if previous_height is not None and previous_height > 0:
                height_ratio = current_height / previous_height
                
                # 检测跌倒：高度下降超过阈值（30%）
                if height_ratio < self.fall_threshold_height_ratio:
                    # 额外验证：检查身体方向
                    is_horizontal = self._is_body_horizontal(skeleton_data)
                    
                    if is_horizontal:
                        # 计算置信度：下降越多，置信度越高
                        confidence = 1.0 - height_ratio
                        self.fall_detection_count += 1
                        
                        return FallEvent(
                            detected=True,
                            confidence=min(confidence, 1.0),
                            timestamp=skeleton_data.timestamp,
                            skeleton_data=skeleton_data
                        )
        
        return FallEvent(detected=False, confidence=0.0, timestamp=skeleton_data.timestamp)
    
    def _calculate_body_height(self, skeleton_data: SkeletonData) -> Optional[float]:
        """
        计算身体高度（从臀部到头部）
        
        Args:
            skeleton_data: 骨骼数据
            
        Returns:
            身体高度或None
        """
        from app.schemas.core import JointType
        
        # 查找关键关节
        head_y = None
        hip_y = None
        
        for kp in skeleton_data.keypoints:
            if kp.joint_type == JointType.NOSE:
                head_y = kp.y
            elif kp.joint_type in [JointType.LEFT_HIP, JointType.RIGHT_HIP]:
                if hip_y is None:
                    hip_y = kp.y
                else:
                    hip_y = (hip_y + kp.y) / 2  # 平均两个臀部
        
        if head_y is not None and hip_y is not None:
            # 高度 = 臀部y - 头部y（y坐标向下增加）
            return abs(hip_y - head_y)
        
        return None
    
    def _is_body_horizontal(self, skeleton_data: SkeletonData) -> bool:
        """
        检查身体是否处于水平状态
        
        Args:
            skeleton_data: 骨骼数据
            
        Returns:
            True如果身体水平
        """
        from app.schemas.core import JointType
        
        # 查找肩膀和臀部
        shoulder_y = None
        hip_y = None
        
        for kp in skeleton_data.keypoints:
            if kp.joint_type in [JointType.LEFT_SHOULDER, JointType.RIGHT_SHOULDER]:
                if shoulder_y is None:
                    shoulder_y = kp.y
                else:
                    shoulder_y = (shoulder_y + kp.y) / 2
            elif kp.joint_type in [JointType.LEFT_HIP, JointType.RIGHT_HIP]:
                if hip_y is None:
                    hip_y = kp.y
                else:
                    hip_y = (hip_y + kp.y) / 2
        
        if shoulder_y is not None and hip_y is not None:
            # 如果肩膀和臀部的y坐标差异很小，身体是水平的
            vertical_diff = abs(shoulder_y - hip_y)
            return vertical_diff < 50  # 阈值：50像素
        
        return False
    
    def ensure_privacy_compliance(self, data: any) -> bool:
        """
        确保数据符合隐私要求
        
        Args:
            data: 待验证的数据
            
        Returns:
            True如果合规
        """
        validation = self.privacy_engine.validate_data_transmission(data)
        
        if not validation.is_valid:
            # 记录违规并阻止操作
            print(f"Privacy compliance check failed: {validation.violations}")
            return False
        
        return True
    
    def _handle_processing_failure(self, error: Exception):
        """
        处理处理失败 - 降级模式
        
        降级策略：
        1. 停止视频处理
        2. 清除所有缓存数据
        3. 记录错误但不损害隐私
        4. 通知系统管理员
        
        Args:
            error: 异常对象
        """
        print(f"Edge processing failure: {error}")
        
        # 进入降级模式
        if isinstance(error, PrivacyViolationError):
            self.degraded_mode_handler.enter_degraded_mode(DegradedModeReason.PRIVACY_VIOLATION)
        else:
            self.degraded_mode_handler.enter_degraded_mode(DegradedModeReason.PROCESSING_ERROR)
        
        # 停止处理
        self.is_running = False
        
        # 清除敏感数据
        self.previous_skeleton = None
        
        # 生成合规报告
        compliance_report = self.privacy_engine.audit_privacy_compliance()
        
        if compliance_report["compliance_status"] != "compliant":
            print("WARNING: Privacy compliance issues detected during failure")
            print(f"Violations: {compliance_report['privacy_violations']}")
    
    def set_cloud_connection_status(self, connected: bool):
        """
        设置云连接状态
        
        Args:
            connected: True如果连接到云端
        """
        previous_status = self.cloud_connected
        self.cloud_connected = connected
        
        if not connected and previous_status:
            # 连接丢失，进入降级模式
            print("[EdgeProcessor] Cloud connection lost, entering degraded mode")
            self.degraded_mode_handler.enter_degraded_mode(DegradedModeReason.NETWORK_FAILURE)
        elif connected and not previous_status:
            # 连接恢复，退出降级模式并同步数据
            print("[EdgeProcessor] Cloud connection restored, syncing buffered data")
            self.degraded_mode_handler.exit_degraded_mode()
            self._sync_buffered_data()
    
    def process_with_fallback(self, skeleton_data: SkeletonData) -> bool:
        """
        处理骨骼数据，支持降级模式
        
        如果云端不可用，数据会被缓冲到本地
        
        Args:
            skeleton_data: 骨骼数据
            
        Returns:
            True如果成功处理或缓冲
        """
        # 验证隐私合规
        if not skeleton_data.anonymized:
            print("[EdgeProcessor] ERROR: Cannot process non-anonymized data")
            return False
        
        if self.cloud_connected:
            # 正常模式：尝试发送到云端
            try:
                success = self._send_to_cloud(skeleton_data)
                if success:
                    return True
                else:
                    # 发送失败，进入降级模式
                    self.set_cloud_connection_status(False)
                    return self.degraded_mode_handler.buffer_skeleton_data(skeleton_data)
            except Exception as e:
                print(f"[EdgeProcessor] Cloud send error: {e}")
                self.set_cloud_connection_status(False)
                return self.degraded_mode_handler.buffer_skeleton_data(skeleton_data)
        else:
            # 降级模式：缓冲数据
            return self.degraded_mode_handler.buffer_skeleton_data(skeleton_data)
    
    def process_incident_with_fallback(self, incident: IncidentData) -> bool:
        """
        处理事件数据，支持降级模式
        
        紧急事件会被优先处理，如果云端不可用则缓冲
        
        Args:
            incident: 事件数据
            
        Returns:
            True如果成功处理或缓冲
        """
        if self.cloud_connected:
            # 正常模式：尝试发送到云端
            try:
                success = self._send_incident_to_cloud(incident)
                if success:
                    return True
                else:
                    # 发送失败，缓冲数据
                    self.set_cloud_connection_status(False)
                    return self.degraded_mode_handler.buffer_incident_data(incident)
            except Exception as e:
                print(f"[EdgeProcessor] Cloud send error for incident: {e}")
                self.set_cloud_connection_status(False)
                return self.degraded_mode_handler.buffer_incident_data(incident)
        else:
            # 降级模式：缓冲数据
            return self.degraded_mode_handler.buffer_incident_data(incident)
    
    def _send_to_cloud(self, skeleton_data: SkeletonData) -> bool:
        """
        发送骨骼数据到云端
        
        注意：这是一个模拟实现。实际实现会使用WebSocket或HTTP API
        
        Args:
            skeleton_data: 骨骼数据
            
        Returns:
            True如果成功发送
        """
        # 模拟实现
        # 实际实现：
        # encrypted_data = self.privacy_engine.encrypt_skeleton_data(skeleton_data)
        # response = self.cloud_client.send(encrypted_data)
        # return response.status_code == 200
        
        return self.cloud_connected
    
    def _send_incident_to_cloud(self, incident: IncidentData) -> bool:
        """
        发送事件数据到云端
        
        Args:
            incident: 事件数据
            
        Returns:
            True如果成功发送
        """
        # 模拟实现
        return self.cloud_connected
    
    def _sync_buffered_data(self):
        """同步缓冲数据到云端"""
        def cloud_sync_callback(buffered_data):
            """云端同步回调"""
            try:
                # 模拟云端同步
                # 实际实现会根据data_type调用相应的API
                return self.cloud_connected
            except Exception as e:
                print(f"[EdgeProcessor] Sync error: {e}")
                return False
        
        stats = self.degraded_mode_handler.sync_buffered_data(cloud_sync_callback)
        print(f"[EdgeProcessor] Sync complete: {stats}")
        
        self.last_cloud_sync_attempt = datetime.utcnow()
    
    def get_processing_stats(self) -> dict:
        """
        获取处理统计信息
        
        Returns:
            统计信息字典
        """
        skeleton_stats = self.skeleton_extractor.get_performance_stats()
        compliance_report = self.privacy_engine.audit_privacy_compliance()
        degraded_status = self.degraded_mode_handler.get_status()
        
        return {
            "frames_processed": self.frame_count,
            "falls_detected": self.fall_detection_count,
            "skeleton_extraction": skeleton_stats,
            "privacy_compliance": compliance_report["compliance_status"],
            "privacy_violations": len(compliance_report["privacy_violations"]),
            "is_running": self.is_running,
            "cloud_connected": self.cloud_connected,
            "degraded_mode": degraded_status
        }
    
    def stop(self):
        """停止视频处理"""
        self.is_running = False
