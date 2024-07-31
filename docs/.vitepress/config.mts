import { defineConfig } from 'vitepress'


// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "VideoFusion",
  description: "A Video Tools",
  cleanUrls: true,
  base: '/VideoFusion/',
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '联系我', link: '/contact_me' },
      { text: '更新日志', link: '/CHANGLOG' }
    ],
    logo: '/logo.png',

    sidebar: [
      {
        text: '导览',
        items: [
          { text: '快速开始', link: '/quick-start.md' },
          { text: '为什么选择 VideoFusion ?', link: '/about.md' },

        ]
      },
      {
        text: '设置',
        items: [
          { text: '常规设置', link: '/normal_settings.md' },
          { text: '高级设置', link: '/advanced_settings.md' },
          { text: 'OpenCV引擎下专属设置', link: '/opencv_only_settings.md' },
        ]
      },
      {
        text: '更多',
        items: [
          { text: '更新日志', link: '/CHANGLOG.md' },
          { text: '联系我', link: '/contact_me.md' },
          { text: '捐赠', link: '/donated.md' },
        ]
      }
    ],


    socialLinks: [
      { icon: 'github', link: 'https://github.com/271374667/VideoFusion' }
    ],

    search: {
          provider: 'local'
        },
    outline: {
      level: 'deep',
      label: '目录'
    }
  
  }
})
