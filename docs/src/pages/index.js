import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

const docs = [
  {
    title: '架构设计文档',
    description: 'AI Studio 的实施蓝图，定义平台三层架构、双平面边界、runtime、tool mesh、DataOps 和部署基线。',
    to: '/docs/application/base_project/architecture_design',
  },
  {
    title: '技术栈',
    description: '收口 AI Studio 当前采用的核心技术栈，以及每一层技术组件的职责边界。',
    to: '/docs/application/base_project/technology_stack',
  },
  {
    title: 'Memory OS 设计',
    description: '定义混合记忆系统，包括 working memory、episodic memory、semantic memory 和 graph memory。',
    to: '/docs/application/base_project/memory_os_design',
  },
];

export default function Home() {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout
      title={siteConfig.title}
      description="AI Studio 文档站"
    >
      <main style={{ maxWidth: 1040, margin: '0 auto', padding: '72px 24px 96px' }}>
        <div style={{ maxWidth: 760, marginBottom: 40 }}>
          <h1 style={{ marginBottom: 16 }}>AI Studio</h1>
          <p style={{ fontSize: '1.1rem', lineHeight: 1.8, marginBottom: 24 }}>
            面向知识、技能、工具网格与混合记忆系统的 LangGraph-first AgentOS 平台文档站。
          </p>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <Link className="button button--primary button--lg" to="/docs/application/base_project">
              打开文档
            </Link>
            <Link className="button button--secondary button--lg" to="/docs/application/base_project/architecture_design">
              查看架构
            </Link>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 20 }}>
          {docs.map((doc) => (
            <Link
              key={doc.title}
              to={doc.to}
              style={{
                display: 'block',
                padding: 24,
                borderRadius: 16,
                textDecoration: 'none',
                border: '1px solid rgba(15, 107, 76, 0.12)',
                background: 'rgba(255,255,255,0.72)',
                color: 'inherit',
              }}
            >
              <h2 style={{ marginBottom: 12, fontSize: '1.1rem' }}>{doc.title}</h2>
              <p style={{ margin: 0, lineHeight: 1.7 }}>{doc.description}</p>
            </Link>
          ))}
        </div>
      </main>
    </Layout>
  );
}
