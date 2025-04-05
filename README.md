# 微信小程序图片压缩工具

这个工具用于压缩微信小程序中的图片，以减小代码包大小，避免超过微信小程序的2MB限制。

## 使用方法

1. 安装依赖：
```bash
npm install
```

2. 运行压缩脚本：
```bash
npm run compress
```

3. 压缩后的图片将保存在 `images` 目录中，文件名前缀为 `compressed_`

4. 检查压缩后的图片质量，如果满意，可以替换原始图片：
```bash
# 在macOS/Linux上
for f in images/compressed_*; do mv "$f" "images/$(basename ${f#images/compressed_})"; done

# 在Windows上
ren images\compressed_* *.*
```

## 微信小程序代码包大小优化建议

1. **压缩图片**：使用此工具压缩图片，将图片大小控制在合理范围内（建议每张图片不超过50KB）

2. **使用CDN**：对于大图片，可以考虑使用CDN加载，而不是直接包含在代码包中

3. **删除未使用的资源**：检查并删除未使用的图片和其他资源

4. **分包加载**：对于较大的应用，可以使用微信小程序的分包加载功能
   - 主包：包含首页和登录页面
   - 分包1：个人中心页面
   - 分包2：奖章页面

5. **使用webp格式**：webp格式通常比PNG和JPEG更小，可以考虑将图片转换为webp格式

6. **优化代码**：删除未使用的代码，压缩JavaScript代码

## 微信小程序代码包大小限制

- 整个小程序所有分包大小不超过 20MB
- 单个分包/主包大小不超过 2MB
- 单个分包/主包大小超过 2MB 时，将无法上传

## 分包加载说明

本项目已经配置了分包加载，将部分页面移到了分包中，以减小主包大小。分包配置如下：

```json
{
  "pages": [
    "pages/index/index",
    "pages/profile/profile",
    "pages/login/login"
  ],
  "subpackages": [
    {
      "root": "pages/medals",
      "pages": [
        "index"
      ]
    }
  ]
}
``` 