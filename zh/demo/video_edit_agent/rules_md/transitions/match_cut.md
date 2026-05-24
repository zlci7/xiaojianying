# 匹配剪辑 - 动接动

**分类:** transition

**描述:** 利用前后镜头运动方向一致实现无缝转场

## 参数

- `motion_tolerance`: 15
- `min_match_duration`: 0.3

## 实现

- 引擎: moviepy
- 方法: composite_with_blend

## 使用建议

**适用场景:** 动作衔接, 行走跟拍切换

**避免使用:** 前后运动方向相反, 速度差异过大
