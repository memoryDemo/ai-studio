// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const { ProvidePlugin } = require("webpack");
// const lightCodeTheme = require('prism-react-renderer/themes/github');
// const darkCodeTheme = require('prism-react-renderer/themes/dracula');
const {themes} = require('prism-react-renderer');
const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;
const isDev = process.env.NODE_ENV === "development";
const isBuildFast = !!process.env.BUILD_FAST;
const isVersioningDisabled = !!process.env.DISABLE_VERSIONING;
const versions = require("./versions.json");
const hasPublishedVersions = Array.isArray(versions) && versions.length > 0;

function isPrerelease(version) {
  return (
    version.includes('-') ||
    version.includes('alpha') ||
    version.includes('beta') ||
    version.includes('rc')
  );
}

function getLastStableVersion() {
  if (!versions || versions.length === 0) {
    return "current";
  }
  const lastStableVersion = versions.find((version) => !isPrerelease(version));
  if (!lastStableVersion) {
    return "current";
  }
  return lastStableVersion;
}

function getNextVersionName() {
  return 'v1';
}

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'AI Studio',
  tagline: '面向知识、技能、工具网格与混合记忆系统的 LangGraph-first AgentOS 平台',
  favicon: 'img/umber-favicon.svg',

  // Set the production url of your site here
  url: 'https://docs.ai-studio.local',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'ai-studio', // Usually your GitHub org/user name.
  projectName: 'ai-studio', // Usually your repo name.

  onBrokenLinks: isDev ? 'throw' : 'warn',

  i18n: {
    defaultLocale: 'zh-CN',
    locales: ['zh-CN'],
  },

  scripts: [
    {
      src: '/redirect.js',
      async: true,
    },
  ],

  clientModules: [
    require.resolve('./src/clientModules/mermaidZoom.js'),
  ],

  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: isDev ? 'throw' : 'warn',
    },
  },

  themes: [
    '@docusaurus/theme-mermaid',
    '@easyops-cn/docusaurus-search-local',
  ],

  plugins: [
    () => ({
      name: "custom-webpack-config",
      configureWebpack: () => ({
        ignoreWarnings: [
          (warning) =>
            typeof warning?.module?.resource === "string" &&
            warning.module.resource.includes(
              "vscode-languageserver-types/lib/umd/main.js",
            ) &&
            /Critical dependency/.test(warning.message || ""),
        ],
        plugins: [
          new ProvidePlugin({
            process: require.resolve("process/browser"),
          }),
        ],
        resolve: {
          fallback: {
            path: false,
            url: false,
          },
        },
        module: {
          rules: [
            {
              test: /\.m?js/,
              resolve: {
                fullySpecified: false,
              },
            },
            {
              test: /\.py$/,
              loader: "raw-loader",
              resolve: {
                fullySpecified: false,
              },
            },
            {
              test: /\.ipynb$/,
              loader: "raw-loader",
              resolve: {
                fullySpecified: false,
              },
            },
          ],
        },
      }),
    }),
  ],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          includeCurrentVersion: true,
          // lastVersion: "current",
          lastVersion: isDev || isBuildFast || isVersioningDisabled ? "current" : getLastStableVersion(),
          onlyIncludeVersions: (() => {
            if (isBuildFast) {
                return ['current'];
            } else if (!isVersioningDisabled && (isDev)) {
              return ['current', ...versions.slice(0, 2)];
            }
            return undefined;
          })(),
          versions: {
            current: {
              label: `${getNextVersionName()}`,
            },
          },
          remarkPlugins: [
            [require("@docusaurus/remark-plugin-npm2yarn"), { sync: true }],
          ],

          async sidebarItemsGenerator({
            defaultSidebarItemsGenerator,
            ...args
          }){
            const sidebarItems = await defaultSidebarItemsGenerator(args);
            sidebarItems.forEach((subItem) => {
              // This allows breaking long sidebar labels into multiple lines
              // by inserting a zero-width space after each slash.
              if (
                "label" in subItem &&
                subItem.label &&
                subItem.label.includes("/")
              ){
                subItem.label = subItem.label.replace("/\//g", "\u200B");
              }
            });
            return sidebarItems;
          }
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
        },

        pages: {
          remarkPlugins: [require("@docusaurus/remark-plugin-npm2yarn")],
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      defaultClassicDocs: '/docs/application/base_project',
      // Replace with your project's social card
      navbar: {
        hideOnScroll: true,
        logo: {
          alt: 'AI Studio Logo',
          src: 'img/umber-logo.svg',
          srcDark: 'img/umber-logo-dark.svg',
          href: "/docs/application/base_project"
        },

        items: [
          {
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: '文档',
            to: "/docs/application/base_project",
          },
          ...(!isVersioningDisabled && hasPublishedVersions
            ? [
                {
                  type: "docsVersionDropdown",
                  position: "right",
                  dropdownItemsAfter: [{to: '/versions', label: 'All versions'}],
                  dropdownActiveClassDisabled: true,
                },
              ]
            : []),
        ],
      },
      footer: {
        style: 'light',
        links: [
          {
            title: '文档',
            items: [
              {
                label: '基座项目总览',
                to: '/docs/application/base_project',
              },
            ],
          },
          {
            title: "平台框架",
            items: [
              {
                label: '架构设计文档',
                to: '/docs/application/base_project/architecture_design',
              },
              {
                label: "技术栈",
                to: '/docs/application/base_project/technology_stack',
              },
              {
                label: "Memory OS 设计",
                to: '/docs/application/base_project/memory_os_design',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} AI Studio`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: false,
      },
    }),
};

module.exports = config;
