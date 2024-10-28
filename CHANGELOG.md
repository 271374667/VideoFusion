# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.12.5](https://github.com/271374667/VideoMosaic/compare/v1.12.2...v1.12.5) - 2024-08-01

- Fix: 修复了任务恢复系统在找不到本地文件的时候会报错的bug [`147ef46`](https://github.com/271374667/VideoMosaic/commit/147ef4631b06716177f0e31479b071809ac0fa14)
- Ui: 现在第一次进入设置页面不会再弹出显示当前引擎的弹窗 [`9398b4b`](https://github.com/271374667/VideoMosaic/commit/9398b4b7b0598a579162602a5b78521f0842f2a0)
- Docs: 修复了徽章版本不显示的bug [`3392e88`](https://github.com/271374667/VideoMosaic/commit/3392e883e92de836a2262f373f55a6a9999b8c11)
- Docs: 完善了README的介绍，修改了徽章显示不了的问题 [`7b49364`](https://github.com/271374667/VideoMosaic/commit/7b49364cfdd18bc406c86487cf63d69493dfd918)
- Docs: 修改README内结构逻辑 [`567d805`](https://github.com/271374667/VideoMosaic/commit/567d805cc4839aef5db8bab98a8c05eee1ae33c1)
- Docs: 移动README里面的捐赠到文档当中，让README拥有更加一致的阅读体验 [`4f78b76`](https://github.com/271374667/VideoMosaic/commit/4f78b762a36810b68f8eb9621122e143bf534bd4)
- Docs: 修改文档里面github跳转为当前项目(之前是跳到个人仓库) [`4e8bfed`](https://github.com/271374667/VideoMosaic/commit/4e8bfedbaa5e1beed64e6a8facfe778b4cf7b6eb)
- Fix: 通过固定窗体大小修复了在运行完毕之后窗口会“长高”的bug [`14b8cc9`](https://github.com/271374667/VideoMosaic/commit/14b8cc901d3a4634b2aff542d8a656308bf7358a)
- Docs: 修复了文档内图片失效的问题以及README文字居中问题 [`24fd63f`](https://github.com/271374667/VideoMosaic/commit/24fd63f0be6a2ce1c60a9f0d158ea4d9b05f6a99)
- Docs: 优化了 README 以及文档 [`ede6b91`](https://github.com/271374667/VideoMosaic/commit/ede6b915a707f4846dd8962ee29a56b163d9c72c)
- Docs: 优化了 README 以及文档 [`bcbd0ce`](https://github.com/271374667/VideoMosaic/commit/bcbd0ce028cf1548743989fefc4190eb7232bfcf)
- Fix: 修复了开始一个空任务导致提示输入视频不能为空的bug [`091a9d6`](https://github.com/271374667/VideoMosaic/commit/091a9d6049e23b75744d38cd0a54affc7d258978)

## [v1.12.2](https://github.com/271374667/VideoMosaic/compare/v1.11.12...v1.12.2) - 2024-07-31

- Fix: 修复了H265格式下过于先进的参数会导致有一些老旧视频无法支持的bug(已经退回到更加兼容的参数) [`99ad599`](https://github.com/271374667/VideoMosaic/commit/99ad599543fab83b0b2e70ed6d21dc93c648a4fd)
- Feature: 主页删除视频时预览画面现在会实时刷新 [`02f8c2b`](https://github.com/271374667/VideoMosaic/commit/02f8c2b348fba7450d128fafbf1cbedbc53d5224)
- Docs: 更新了文档视频顺序调整的部分 [`fcd1c39`](https://github.com/271374667/VideoMosaic/commit/fcd1c3991604785e70117933d6db346990b7a95a)
- Modify: 修改vitepress的base为VideoFusion [`7d036c7`](https://github.com/271374667/VideoMosaic/commit/7d036c7f3ab80e125dfa44394ffb073977afab8d)
- Remove: 删除vitepress的base [`5c84fa7`](https://github.com/271374667/VideoMosaic/commit/5c84fa72d098021f3f12c2ef15b63d44d79ad87c)
- Action: 修改pnpm大版本号为9 [`981ad52`](https://github.com/271374667/VideoMosaic/commit/981ad5211d0174f0af4f5f05e27b3dfa2d55a09b)
- Action: 试图让action能够识别pnpm-lock.yaml [`0886911`](https://github.com/271374667/VideoMosaic/commit/08869114d7a51261bfab7641ee2102ba493d98bd)
- Action: 修改pnpm的版本为9 [`7ee8a1d`](https://github.com/271374667/VideoMosaic/commit/7ee8a1dba3853057732f4c892813683a1d866c2d)
- Action: 指定了pnpm的版本 [`5666ff5`](https://github.com/271374667/VideoMosaic/commit/5666ff56ace9fc428e739ca39cb248af45d0187e)
- Fix: 修复因为package.json不存在导致构建失败的bug [`f2d284c`](https://github.com/271374667/VideoMosaic/commit/f2d284c587def4f02f38993f26712963a720094d)
- Action: 修改action中npm为pnpm [`599feb7`](https://github.com/271374667/VideoMosaic/commit/599feb717a0c578cf1a369ae263dbd397755f347)
- Optimization: 现在设置页面如果不是静态去黑边模式则视频采样率滑条会保存不可选状态 [`42c5367`](https://github.com/271374667/VideoMosaic/commit/42c536779fdcb90aa4cf7ef0a28a603d5d843f55)
- Optimization: 优化了报错页面的报错捕获条件 [`c5fb666`](https://github.com/271374667/VideoMosaic/commit/c5fb666f7ea3045bae2994720cd1481800ada1a8)
- Optimization: 优化了重新编译的参数，现在H265等其他编码器也有更好的效果 [`d9dc12f`](https://github.com/271374667/VideoMosaic/commit/d9dc12f60b4725217277a24bd2fcfb13caa8ccc9)
- Modify: 现在设置页面中仅OpenCV支持的功能被单独移动到了新的分组方便区分 [`ec14943`](https://github.com/271374667/VideoMosaic/commit/ec149434cfa59d1b0f52f2796d5c320382a57f15)

## [v1.11.12](https://github.com/271374667/VideoMosaic/compare/v1.0.0...v1.11.12) - 2024-07-29

- Feature: 显示了备份恢复，如果上一次任务没有完成将会自动恢复上一次的任务 [`05d7d3a`](https://github.com/271374667/VideoMosaic/commit/05d7d3a23f08952ab59cc54a48d189d15e1d0b84)
- Feature: 完整实现了FFmpegEngine [`640833d`](https://github.com/271374667/VideoMosaic/commit/640833da496d140a2a7f33db53d3fdbaa72f0397)
- Feature: 使用策略模式分离VideoEngine，现在OpenCV和FFmpeg都有自己的方法 [`31ab275`](https://github.com/271374667/VideoMosaic/commit/31ab27591f64845648ecf52903f70ca4cfe59f33)
- Feature: 现在设置页面里面选择使用FFmpeg引擎会默认关闭不支持的处理器 [`80d8b4d`](https://github.com/271374667/VideoMosaic/commit/80d8b4dc966cbd60ba105f016b073d8d70765568)
- Feature: 设置页面的版本更新说明使用了新的messagebox提示框 [`4513ed9`](https://github.com/271374667/VideoMosaic/commit/4513ed9dab8c4b6fb40c3abc06b68b6526c9d74e)
- Feature: 新增处理模式,未来可以选择使用什么引擎处理视频(ffmpeg,opencv) [`7f3c11b`](https://github.com/271374667/VideoMosaic/commit/7f3c11bb4c4fe93dadbeb6e0ccbc2aad29bdcbfa)
- Fix: 修复了多个视频合并的时候crop_processor剪裁会出现错误 [`6696f8c`](https://github.com/271374667/VideoMosaic/commit/6696f8ce1a2073d05f90808c9cf10f5b99238575)

## [v1.0.0](https://github.com/271374667/VideoMosaic/compare/v0.32.4...v1.0.0) - 2024-07-24

- Feature: 现在会自动为没有音频轨道的视频添加音频 [`82d0b20`](https://github.com/271374667/VideoMosaic/commit/82d0b20f1850c4d87eee26719fabb04829f6fef0)
- Feature: 现在软件的使用时间会在日志中输出 [`af020ec`](https://github.com/271374667/VideoMosaic/commit/af020ec9be0e42b49740745a1cb5562b3479dd86)
- Feature: 添加了一个真正的中断子线程的方法 [`e3022a1`](https://github.com/271374667/VideoMosaic/commit/e3022a1189f3465ace5c499f0414a2aebe332dd7)
- Remove: 删除了无用了函数 [`733aeb2`](https://github.com/271374667/VideoMosaic/commit/733aeb22bcae842e25b7b892e1477e9d697bf3ec)
- Fix: 修复了即使不勾选删除临时文件夹也会导致文件夹被删除的bug [`1e98c52`](https://github.com/271374667/VideoMosaic/commit/1e98c52fab01d3fe6bf3a9773b7778a803017e02)
- Fix: 修复了退出后无法删除临时文件夹的bug [`fdfb5a0`](https://github.com/271374667/VideoMosaic/commit/fdfb5a0c251e509610d679e4e57041e74cb3fb0c)
- Refactor: program_coordinator模块实现了基本功能 [`bc92ba7`](https://github.com/271374667/VideoMosaic/commit/bc92ba7895d2247742bc00ed1f8c2bbdabe2fc26)
- Feature: 新增白平衡 [`545e05c`](https://github.com/271374667/VideoMosaic/commit/545e05c574709ad14eeaf86ec0671d650f4d6c51)
- Feature: 新增了音频降噪处理器 [`6c76102`](https://github.com/271374667/VideoMosaic/commit/6c76102a0512f5fce422c320d1e4f96970db3b7f)
- Feature: 新增一个线程超时自动杀死的函数 [`896c94f`](https://github.com/271374667/VideoMosaic/commit/896c94f0bdd14aef7a2ac87579f3c622126d6976)
- Refactor: 重构了剪裁处理器 [`8cbdcb6`](https://github.com/271374667/VideoMosaic/commit/8cbdcb640dd632194234230a907f8e285b19582b)
- Feature: 新增ESPCN视频超分AI模型以及处理器 [`c49b4ef`](https://github.com/271374667/VideoMosaic/commit/c49b4ef80ab56e2f85c8df7df3da3d9fb9ec4fbf)
- Feature: 新增白平衡处理器 [`c34baae`](https://github.com/271374667/VideoMosaic/commit/c34baae91c9a178421acfe51ce0a692e66c81600)
- Feature: 新增了命令行调用方式 [`e86d5c4`](https://github.com/271374667/VideoMosaic/commit/e86d5c4a195ddf691cc3c5e8729060c4026944ef)

## [v0.32.4](https://github.com/271374667/VideoMosaic/compare/v0.30.5...v0.32.4) - 2024-07-06

- Dependence: 更新了nuitka和fluent-widget相关依赖 [`cc5b21c`](https://github.com/271374667/VideoMosaic/commit/cc5b21ce14767d903d3988e3ef60dcbb4df965ec)
- Feature: 新增失败提示条,程序出错之后会在主页面弹出提示条进行提醒 [`cdd175f`](https://github.com/271374667/VideoMosaic/commit/cdd175f60a394f89caa1a20e65c6855f2580057b)
- Feature: 现在会检测ffprobe是否能够成功载入 [`a6baa74`](https://github.com/271374667/VideoMosaic/commit/a6baa7401b7fe9d862afc8d21750cf78be91216c)

## [v0.30.5](https://github.com/271374667/VideoMosaic/compare/v0.30.2...v0.30.5) - 2024-06-24

- Fix: 修复了设置页面说明上的一处错误 [`40d55b4`](https://github.com/271374667/VideoMosaic/commit/40d55b4a50077cf25bd865d6e85364f031fc09eb)
- Fix: 修复了在视频剪裁后刚好等于目标分辨率的时候会报错的bug [`cc40971`](https://github.com/271374667/VideoMosaic/commit/cc4097189fdb5e4900861f04fbfb54ef746dfe39)

## [v0.30.2](https://github.com/271374667/VideoMosaic/compare/v0.29.3...v0.30.2) - 2024-06-24

- Modify: hqdn3d视频降噪现在将保持默认开启状态(您可以前往设置页面关闭) [`28221af`](https://github.com/271374667/VideoMosaic/commit/28221afd7061cd30f4b44b0866964754efbcab54)
- Fix: 修复了视频设置了和原视频不同的方向的时候ffmpeg会报错的bug [`f776c46`](https://github.com/271374667/VideoMosaic/commit/f776c468580a3c6d82496f2e934d7be93d838b7f)
- Feature: 为音频采样率在设置页面增加选项,现在可以自行控制音频采样率 [`6b0c2a4`](https://github.com/271374667/VideoMosaic/commit/6b0c2a4a6ff0fb634259af9afaef30246990b3c0)

## [v0.29.3](https://github.com/271374667/VideoMosaic/compare/v0.28.7...v0.29.3) - 2024-06-22

- Feature: 新的报错捕获机制,现在能够直接打印错误信息到命令行 [`bfa93b7`](https://github.com/271374667/VideoMosaic/commit/bfa93b727e2639ad6b666f40e3f3287333ef7a28)

## [v0.28.7](https://github.com/271374667/VideoMosaic/compare/v0.28.6...v0.28.7) - 2024-06-22

- Fix: 修复了每一次处理视频的时候都会有一个一闪而过的命令行的bug [`c8503c0`](https://github.com/271374667/VideoMosaic/commit/c8503c0188c3de7d161d0e1144e87c3e9e43f026)

## [v0.28.6](https://github.com/271374667/VideoMosaic/compare/v0.24.12...v0.28.6) - 2024-06-22

- Feature: 现在可以使用退格或者Delete键快捷删除视频列表内的视频 [`f2699f4`](https://github.com/271374667/VideoMosaic/commit/f2699f48feb77ecbf0148629a1e4082c636f72c2)
- Feature: 现在可以使用退格或者Delete键快捷删除视频列表内的视频 [`0b106e1`](https://github.com/271374667/VideoMosaic/commit/0b106e1e0886f1dc009eedb2a6e9239461462521)
- Feature: 现在视频合并的阶段也拥有了独立的进度条 [`d294364`](https://github.com/271374667/VideoMosaic/commit/d2943641f268330fb7842002604a40b2ad813b4d)
- Docs: 更新了README [`faf2ebf`](https://github.com/271374667/VideoMosaic/commit/faf2ebfd44db8c11b1e9ad376c24f62ee561e7e7)
- Docs: 更新了README里面落后的图片，以及一些补充性说明 [`9ec3e19`](https://github.com/271374667/VideoMosaic/commit/9ec3e19ac6703ad76fa9f753d0f9b32e55e4e857)

## [v0.24.12](https://github.com/271374667/VideoMosaic/compare/v0.24.8...v0.24.12) - 2024-06-20

- Fix: 修复了因为文件权限不足导致无法继续合并文件的bug [`9b65a12`](https://github.com/271374667/VideoMosaic/commit/9b65a12a30a1240409d08d76717b8d0ef0d689d3)

## [v0.24.8](https://github.com/271374667/VideoMosaic/compare/v0.21.3...v0.24.8) - 2024-06-20

- Fix: 修复了没有视频合成视频后也能进行合成的bug [`c114da8`](https://github.com/271374667/VideoMosaic/commit/c114da855a844111e6d1e3e36a5424de50773a4a)
- Feature: 现在可以通过限制视频的最大去黑边帧数来防止长视频一直进行重复的黑边去除 [`b98e496`](https://github.com/271374667/VideoMosaic/commit/b98e496af35b19477a2e0b6801adab8999793976)
- Feature: 现在使用soxr来对音频重新编码，能更好的防止出现尖锐噪音 [`85a740f`](https://github.com/271374667/VideoMosaic/commit/85a740fa6548f2bb1a821b504d495decb0de2739)
- Feature: 现在可供合成的视频数量不再受命令行长度限制 [`e2432cc`](https://github.com/271374667/VideoMosaic/commit/e2432cc9f0fbc7e02010b6130c1fc6148f98aa9a)

## [v0.21.3](https://github.com/271374667/VideoMosaic/compare/v0.20.1...v0.21.3) - 2024-06-05

- Fix: 为检查更新更新了多线程,修复了进行网络请求的时候会卡死的bug [`b60781d`](https://github.com/271374667/VideoMosaic/commit/b60781d55bf8452f388c1af9efc8f008b1efe0b8)
- Feature: 在设置页面为程序新增了检查更新功能,现在可以知道当前软件是否是最新版本 [`be2fff9`](https://github.com/271374667/VideoMosaic/commit/be2fff910f3b6c94ba2d6cb654f3a89908cce881)
- Fix: 修复了点击视频有时候会长时间卡死的bug [`ce597b9`](https://github.com/271374667/VideoMosaic/commit/ce597b945ec510117924a12b8ea55b0b889cc518)

## [v0.20.1](https://github.com/271374667/VideoMosaic/compare/v0.18.2...v0.20.1) - 2024-06-04

- Feature: 现在的视频列表文件框支持删除单个视频(右键菜单) [`7f72f19`](https://github.com/271374667/VideoMosaic/commit/7f72f199246eb87a3e037b34e300a0b1ee92b3a3)

## [v0.18.2](https://github.com/271374667/VideoMosaic/compare/v0.17.7...v0.18.2) - 2024-06-04

- Modify: 现在默认去黑边算法改为动态去黑边(采样率为10) [`51b1ea5`](https://github.com/271374667/VideoMosaic/commit/51b1ea5af586f9b8027168e7ad9c622c861a3a90)
- Feature: 新增动态去除视频黑边算法,通过绘制所有发生变动的像素来判断视频主体画面,适合黑边不明显的视频 [`c0c9b6b`](https://github.com/271374667/VideoMosaic/commit/c0c9b6b318bcc4f18adcd8c6084d1279b9e4cc98)

## [v0.17.7](https://github.com/271374667/VideoMosaic/compare/v0.13.9...v0.17.7) - 2024-06-03

- Feature: 新的更加美观的关于页面,增加了感谢fluent-widget的作者 [`28357dd`](https://github.com/271374667/VideoMosaic/commit/28357dddf1d41d38831b2fd58d4552799e7632fb)
- Feature: 现在可以去除视频内的色块 [`128cbd4`](https://github.com/271374667/VideoMosaic/commit/128cbd4fd024b7b343655b30450bc614a4fc1083)
- Feature: 现在可以在设置里面设置去除视频的色带 [`a678224`](https://github.com/271374667/VideoMosaic/commit/a678224f2b0a8297b142b27127a0b1fb4cbdd1ad)
- Feature: 新增音频降噪,音频降噪默认有两种模式静态分析和AI模型降噪(推荐,效果好,而且还很快) [`87f4095`](https://github.com/271374667/VideoMosaic/commit/87f40958ee597948db71594b04cd885843259c77)

## [v0.13.9](https://github.com/271374667/VideoMosaic/compare/v0.10.4...v0.13.9) - 2024-06-03

- Feature: 新增音频降噪,音频降噪默认有两种模式静态分析和AI模型降噪(推荐,效果好,而且还很快) [`1179c88`](https://github.com/271374667/VideoMosaic/commit/1179c880d62ff1692b7ddefca8c772efa9212469)
- Feature: 新增了更多能够设置的音频标准化选项，现在可以选择电台/TV/电影等多种音频标准化方案(国标GY/T 377-2023标准) [`0bd52cb`](https://github.com/271374667/VideoMosaic/commit/0bd52cb372ccff3c163dbcc86ccc60ef639b149f)
- Fix: 修复了特定版本下处理视频之后无法继续合并的bug [`7f01487`](https://github.com/271374667/VideoMosaic/commit/7f01487feb415c61ba82bd90d5b89db88be08dd0)
- Docs: 完善了README,现在有了更加高端和正式的说明 [`7854dda`](https://github.com/271374667/VideoMosaic/commit/7854dda62698a4e32ddc5ad33f6eef22da345707)
- Modify: 软件从VideoMosaic更名为VideoFusion [`ab514ba`](https://github.com/271374667/VideoMosaic/commit/ab514ba1155e801391a04d2207d0fc3b89b37989)
- Fix: 修复了程序运行完毕之后不会删除临时文件夹的bug [`1023e2e`](https://github.com/271374667/VideoMosaic/commit/1023e2e906796ce8e6d2f324ca2400437adb6aa2)

## [v0.10.4](https://github.com/271374667/VideoMosaic/compare/v0.9.1...v0.10.4) - 2024-06-01

- Feature: 新增中途取消功能，现在可以随时进行取消 [`0722097`](https://github.com/271374667/VideoMosaic/commit/0722097bbef43dae33c18647e78498bb26de78cc)

## [v0.9.1](https://github.com/271374667/VideoMosaic/compare/v0.8.5...v0.9.1) - 2024-05-30

- Feature: 为预览画面帧增加了多线程，防止卡死页面 [`108de8e`](https://github.com/271374667/VideoMosaic/commit/108de8e8d22a4e8868a37ff0100c227beee9e94b)

## [v0.8.5](https://github.com/271374667/VideoMosaic/compare/v0.5.15...v0.8.5) - 2024-05-28

- Feature: 新的去黑边阈值使用自适应阈值,会比之前更加保守,不会和之前一样剪裁主体画面 [`bb0f278`](https://github.com/271374667/VideoMosaic/commit/bb0f278b9885d495f114cba1ed3516a7ae6d949e)

## [v0.5.15](https://github.com/271374667/VideoMosaic/compare/v0.5.14...v0.5.15) - 2024-05-27

- Feature: 现在的视频列表能够通过拖入txt文件导入视频文件 [`d5abd53`](https://github.com/271374667/VideoMosaic/commit/d5abd5348f48c1eb91ae536ba000e020602ebaa1)

## [v0.5.14](https://github.com/271374667/VideoMosaic/compare/v0.2.3...v0.5.14) - 2024-05-26

- Docs: 完善了README文档 [`c29fcc2`](https://github.com/271374667/VideoMosaic/commit/c29fcc29f1a9e5a268add2d6eee5928ed9dbbd79)
- Feature: 新增一个关于页面,其中包含软件说明 [`82fb3ba`](https://github.com/271374667/VideoMosaic/commit/82fb3ba4435218cc45ca2621d24d0cc2388fd645)
- Refactor: 几乎推翻重写所有内容,目前新功能均已测试并且实现功能 [`c7fe866`](https://github.com/271374667/VideoMosaic/commit/c7fe8666333fd51d40ebc353437ce55210bf4bae)
- Refactor: 分离视频列表 [`66bee48`](https://github.com/271374667/VideoMosaic/commit/66bee481c823395083af694b9d6714b3636c2ade)
- Refactor: 正在将界面重构到fluent-widget [`1d1fe50`](https://github.com/271374667/VideoMosaic/commit/1d1fe50343825f4e590f0d039f8cd4447078548e)
- Feature: 为音频新增对齐，现在视频会根据视频的长度进行对齐，解决长视频音画不同步的情况 [`84e8a87`](https://github.com/271374667/VideoMosaic/commit/84e8a87f793989b9f605edd2799174f8af2877a5)
- Feature: ffmpeg运行命令的时候会先进行命令检查以及文件检查 [`a470f2f`](https://github.com/271374667/VideoMosaic/commit/a470f2f68c61ccc8492cf749bcb0d94f923a431d)
- Ui: 现在的命令行替换成了更加醒目的白色背景 [`13a09ca`](https://github.com/271374667/VideoMosaic/commit/13a09ca054a333f47e58eb1e1f5f85f98ba98bde)
- Feature: 新增了视频压缩(未实装) [`c64fa1f`](https://github.com/271374667/VideoMosaic/commit/c64fa1f6abf90b07f67d6d58906ba98e15dba878)
- Dependence: 为项目添加依赖ffmpeg，同时实现了从ffmpeg中实时获取进度 [`a9e7156`](https://github.com/271374667/VideoMosaic/commit/a9e71566825a0804c2c5aba43c6a8d50dda8ca0a)
- Feature: 现在从曾经的局部补帧抽帧改为全局抽帧和补帧，新的方法更加耗时，但是保证了视频长度不会相差过大，方便后期音频合并 [`9272767`](https://github.com/271374667/VideoMosaic/commit/9272767489bb5d64715d8bc38b8efc6ae3f56448)
- Ui: 为进度条增加更加显眼的组别 [`e85de47`](https://github.com/271374667/VideoMosaic/commit/e85de478fb751f0f93cd1525ac33def18707f7cb)
- Docs: 调整README中图片位置居中 [`ae7b4f1`](https://github.com/271374667/VideoMosaic/commit/ae7b4f1ad2f518c90211755d094309704f3e30a1)
- Docs: 为README增加了更多的说明 [`9c7c836`](https://github.com/271374667/VideoMosaic/commit/9c7c8363b3fc270f9bcb378e2d665d0c0a3b8150)

## v0.2.3 - 2024-05-19

- Initialization: 项目上线(之前项目内有违规信息我删库了) [`c3a4aa9`](https://github.com/271374667/VideoMosaic/commit/c3a4aa9b0bf024db99a79b9bb1f9d86e1b42d872)
