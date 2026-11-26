// Based on dshanpi/Docs, retaining its Docusaurus classic theme and local search.
import {themes as prismThemes} from 'prism-react-renderer';
import originalImages from './plugins/original-images.cjs';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'ROS2 嵌入式机器人教程',
  tagline: '基于 MUSE-PI-PRO 的嵌入式 Linux 与 ROS2 开发教程 · 百问科技',
  favicon: 'img/logo.svg',
  url: process.env.DOCS_SITE_URL || 'https://ros2.100ask.net',
  baseUrl: process.env.DOCS_BASE_URL || '/',
  trailingSlash: true,
  organizationName: 'dshanpi',
  projectName: 'ros2-docs',
  future: {v4: true},
  onBrokenLinks: 'throw',
  onBrokenAnchors: 'throw',
  i18n: {defaultLocale: 'zh-Hans', locales: ['zh-Hans']},
  presets: [['classic', {
    docs: {
      routeBasePath: '/',
      sidebarPath: './sidebars.js',
      editUrl: 'https://github.com/dshanpi/ros2-docs/edit/main/',
      showLastUpdateTime: false,
      beforeDefaultRemarkPlugins: [originalImages],
    },
    blog: false,
    theme: {customCss: './src/css/custom.css'},
    sitemap: {changefreq: 'monthly', priority: 0.5},
  }]],
  markdown: {
    format: 'detect',
    hooks: {onBrokenMarkdownLinks: 'throw', onBrokenMarkdownImages: 'throw'},
  },
  themeConfig: {
    colorMode: {respectPrefersColorScheme: true},
    docs: {sidebar: {autoCollapseCategories: true, hideable: true}},
    tableOfContents: {minHeadingLevel: 2, maxHeadingLevel: 3},
    navbar: {
      title: 'ROS2 教程',
      logo: {alt: '百问科技', src: 'img/manual/image1.png'},
      items: [
        {type: 'docSidebar', sidebarId: 'tutorialSidebar', label: '教程目录', position: 'left'},
        {to: '/chapter-14/', label: 'ROS2 入门', position: 'left'},
        {href: 'https://wiki.dshanpi.org', label: '东山Π 文档', position: 'right'},
        {href: 'https://github.com/dshanpi/ros2-docs', label: 'GitHub', position: 'right'},
      ],
    },
    footer: {
      style: 'dark',
      copyright: `Copyright © ${new Date().getFullYear()} 百问科技 · 100askTeam. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'c', 'cpp', 'python', 'makefile', 'cmake'],
    },
  },
  plugins: [['@easyops-cn/docusaurus-search-local', {
    hashed: true,
    language: ['en', 'zh'],
    indexBlog: false,
    docsRouteBasePath: '/',
    highlightSearchTermsOnTargetPage: true,
    searchResultLimits: 12,
  }]],
};
export default config;
