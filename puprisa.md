## PPS

### 📦 图像数据

| 属性               | 类型              | 说明                                                         |
| ------------------ | ----------------- | ------------------------------------------------------------ |
| `images`           | `np.ndarray` (3D) | 当前显示的图像栈，形状 `(n_frames, height, width)`，已经过背景减法等处理 |
| `image_dimensions` | `tuple`           | 单帧图像的尺寸 `(height, width)`                             |

### ⏱️ 轴
| 属性          | 类型              | 说明                                                         |
| ------------- | ----------------- | ------------------------------------------------------------ |
| `axis_type`   | `str`             | `'time'` 或 `'z'`，标记第三维的含义                          |
| `axis_values` | `np.ndarray` (1D) | 每个图像帧对应的时间延迟（单位 ps）/ 每个图像帧对应的 z 轴位置（单位 µm） |

### 🧹 背景减法
| 属性                      | 类型                        | 说明                                                         |
| ------------------------- | --------------------------- | ------------------------------------------------------------ |
| `_original_images`        | `np.ndarray` 或 `None`      | 原始图像栈副本，用于背景减法重置，形状 `(n_frames, height, width)` |
| `_background_subtraction` | `np.ndarray` (2D) 或 `None` | 背景减法值（多为像素级均值），`self.images = _original_images - _background_subtraction` |

### 🔳 掩膜

| 属性          | 类型                    | 说明                                                         |
| ------------- | ----------------------- | ------------------------------------------------------------ |
| `mask`        | `np.ndarray` (2D, bool) | 当前有效掩模：`_base_mask` 与所有启用掩模层的逻辑与，决定计算中使用的像素 |
| `_base_mask`  | `np.ndarray` (2D, bool) | 基础掩模（可通过阈值分割、手动绘制、`mask_slices` 等方法修改） |
| `mask_layers` | `list` of `dict`        | 掩模层列表（支持多级交互式掩模），每个元素包含 `id`, `label`, `mask` (2D bool), `enabled`, `comment`, `date` |

### 📊 分析结果

| 属性      | 类型   | 说明                                                        |
| --------- | ------ | ----------------------------------------------------------- |
| `results` | `dict` | 存储分析结果（如分类器的 `pigments`、`stats`、`matrix` 等） |

### 📄 元数据

| 属性       | 类型  | 说明                         |
| ---------- | ----- | ---------------------------- |
| `filename` | `str` | 数据来源的文件名或自定义标识 |

## GUI

```
pip install mkdocs-material
pip install mkdocstrings
pip install mkdocstrings-python
```



## Phasor

