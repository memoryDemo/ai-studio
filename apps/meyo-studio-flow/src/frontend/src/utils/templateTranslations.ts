type TemplateDisplayText = {
  name: string;
  description: string;
};

const ZH_TEMPLATE_TEXT: Record<string, TemplateDisplayText> = {
  "Basic Prompt Chaining": {
    name: "基础提示词链",
    description: "将多个提示词按顺序连接，让每一步输出作为下一步输入。",
  },
  "Basic Prompting": {
    name: "基础提示词",
    description: "使用语言模型完成基础提示词调用。",
  },
  "Blog Writer": {
    name: "博客写作",
    description: "根据说明和参考文章自动生成定制化博客文章。",
  },
  "Custom Component Generator": {
    name: "自定义组件生成器",
    description: "按组件规范生成结构清晰的自定义组件代码。",
  },
  "Document Q&A": {
    name: "文档问答",
    description: "结合 PDF 读取和语言模型，回答文档相关问题。",
  },
  "Financial Report Parser": {
    name: "财报解析",
    description: "从财务报告中提取关键指标，并整理成结构化结果。",
  },
  "Hybrid Search RAG": {
    name: "混合搜索 RAG",
    description: "使用向量数据库体验混合搜索增强生成。",
  },
  "Image Sentiment Analysis": {
    name: "图片情感分析",
    description: "分析图片并将其归类为正面、负面或中性。",
  },
  "Instagram Copywriter": {
    name: "Instagram 文案",
    description: "生成社交媒体文案和图片提示词，提升内容创作效率。",
  },
  "Invoice Summarizer": {
    name: "发票摘要",
    description: "提取发票内容并生成清晰摘要。",
  },
  "Knowledge Base": {
    name: "知识库检索",
    description: "在知识库中执行向量搜索，检索相关文档。",
  },
  "Market Research": {
    name: "市场研究",
    description: "调研公司信息，提取关键业务数据并生成结构化结果。",
  },
  "Meeting Summary": {
    name: "会议摘要",
    description: "转录并总结会议内容，快速提炼关键信息。",
  },
  "Memory Chatbot": {
    name: "记忆聊天机器人",
    description: "保存并引用历史消息，让模型在对话中保持上下文。",
  },
  "News Aggregator": {
    name: "新闻聚合",
    description: "从网页中提取数据和信息。",
  },
  "NVIDIA RTX Remix": {
    name: "NVIDIA RTX Remix",
    description: "集成 NVIDIA RTX Remix Toolkit REST API 和相关文档。",
  },
  "Pokédex Agent": {
    name: "图鉴智能体",
    description: "使用专用智能体和 Pokédex API 查询信息。",
  },
  "Portfolio Website Code Generator": {
    name: "作品集网站生成器",
    description: "从简历文档提取结构化信息并生成作品集网站代码。",
  },
  "Price Deal Finder": {
    name: "价格优惠查找",
    description: "跨多个电商平台搜索并比较商品价格。",
  },
  "Research Agent": {
    name: "研究智能体",
    description: "制定研究计划，执行网页搜索，并综合生成报告。",
  },
  "Research Translation Loop": {
    name: "研究翻译循环",
    description: "循环处理搜索结果，并自动翻译每条结果。",
  },
  "SEO Keyword Generator": {
    name: "SEO 关键词生成器",
    description: "根据产品信息、痛点和客户画像生成 SEO 关键词。",
  },
  "SaaS Pricing": {
    name: "SaaS 定价",
    description: "基于成本、利润率和订阅用户数计算 SaaS 定价。",
  },
  "Search agent": {
    name: "搜索智能体",
    description: "在网页上搜索信息。",
  },
  "Sequential Tasks Agents": {
    name: "顺序任务智能体",
    description: "按预设顺序系统执行一系列任务。",
  },
  "Simple Agent": {
    name: "简单智能体",
    description: "一个简单但强大的入门智能体。",
  },
  "Social Media Agent": {
    name: "社交媒体智能体",
    description: "使用工具搜索并分析社交媒体资料。",
  },
  "Text Sentiment Analysis": {
    name: "文本情感分析",
    description: "加载文本数据并使用 AI 分析情感倾向。",
  },
  "Travel Planning Agents": {
    name: "旅行规划智能体",
    description: "创建旅行规划聊天机器人，生成个性化行程。",
  },
  "Twitter Thread Generator": {
    name: "Twitter 长帖生成器",
    description: "将结构化输入转化为符合品牌语调的长帖内容。",
  },
  "Vector Store RAG": {
    name: "向量库 RAG",
    description: "加载数据作为聊天上下文，进行检索增强生成。",
  },
  "YouTube Analysis": {
    name: "YouTube 分析",
    description: "提取视频评论和转录内容，并分析情感与主题。",
  },
};

export const isChineseLanguage = (language?: string) =>
  language?.toLowerCase().startsWith("zh") ?? false;

export const getLocalizedTemplateText = (
  name: string,
  description: string,
  language?: string,
): TemplateDisplayText => {
  if (!isChineseLanguage(language)) {
    return { name, description };
  }

  return ZH_TEMPLATE_TEXT[name] ?? { name, description };
};
