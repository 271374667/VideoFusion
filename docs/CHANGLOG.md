# Changelog

## [v0.32.4] - 2024-07-06

### Added
- 新增失败提示条，程序出错之后会在主页面弹出提示条进行提醒 (cdd175f)。
- 现在会检测ffprobe是否能够成功载入 (a6baa74)。

### Changed
- 更新了nuitka和fluent-widget相关依赖 (cc5b21c)。
- 更新了所有的依赖 (a6baa74)。

### Fixed
- 修复了自动去黑边因为视频剪裁宽高不一致而导致的小概率出现合成失败的bug (cdd175f)。
- 修复了ffprobe载入失败的bug (a6baa74)。

