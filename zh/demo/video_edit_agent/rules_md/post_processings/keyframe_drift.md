# 关键帧漂移

**分类:** post_processing

**描述:** 画面微微缩放/位移增加动感，避免静态画面呆板

## 参数

- `scale_range`: [0.95, 1.05]
- `position_range`: [-10, 10]
- `duration`: per_clip

## 实现

- 引擎: moviepy
- 方法: keyframe_transform

## 使用建议

**适用场景:** 静态镜头, 照片素材

**避免使用:** 已有大幅运动的镜头
