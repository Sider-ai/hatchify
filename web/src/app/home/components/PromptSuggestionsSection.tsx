import type React from "react";
import { useTranslation } from "react-i18next";

const PromptSuggestionsSection: React.FC<{
	onClick: (prompt: string) => void;
}> = ({ onClick }) => {
	const { t, i18n } = useTranslation();
	const promptSuggestions: {
		icon: string;
		title: string;
		prompt: string;
		zhCN_Prompt: string;
	}[] = [
		{
			icon: `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 14 14" fill="none">
  <path d="M7.00065 0.583618C3.45544 0.583618 0.583984 3.45508 0.583984 7.00028C0.583984 9.83966 2.42076 12.2379 4.97138 13.0881C5.29221 13.1442 5.41253 12.9517 5.41253 12.7833C5.41253 12.6309 5.40451 12.1256 5.40451 11.5882C3.79232 11.8849 3.37523 11.1952 3.2469 10.8342C3.17471 10.6497 2.8619 10.0803 2.58919 9.92786C2.36461 9.80758 2.04378 9.51078 2.58117 9.50278C3.08648 9.49473 3.44742 9.96799 3.56773 10.1605C4.14523 11.131 5.06763 10.8583 5.43659 10.6899C5.49273 10.2728 5.66117 9.99203 5.84565 9.83161C4.41794 9.67119 2.92607 9.11778 2.92607 6.66341C2.92607 5.96557 3.17471 5.3881 3.58378 4.93893C3.51961 4.77851 3.29503 4.12081 3.64794 3.23851C3.64794 3.23851 4.18534 3.07008 5.41253 3.89622C5.92586 3.75185 6.47128 3.67966 7.01669 3.67966C7.56211 3.67966 8.10753 3.75185 8.62086 3.89622C9.84808 3.06206 10.3854 3.23851 10.3854 3.23851C10.7384 4.12081 10.5138 4.77851 10.4496 4.93893C10.8587 5.3881 11.1073 5.95758 11.1073 6.66341C11.1073 9.12578 9.60745 9.67119 8.17974 9.83161C8.41232 10.0322 8.61287 10.4172 8.61287 11.0187C8.61287 11.877 8.60482 12.5667 8.60482 12.7833C8.60482 12.9517 8.72516 13.1522 9.04599 13.0881C11.5806 12.2379 13.4173 9.83161 13.4173 7.00028C13.4173 3.45508 10.5459 0.583618 7.00065 0.583618Z" fill="currentColor"/>
</svg>`,
			title: t("home.promptSuggestions.githubTrending"),
			prompt: `Generate a daily GitHub trending analyzer. When run, it should scrape the top 10 trending project names and descriptions on GitHub for that day, then apply category tags and generate a concise, comprehensive analysis.`,
			zhCN_Prompt: `生成一个当日Github趋势分析器，当开始运行的时候，爬取GitHub当日trending前十的项目名称以及简介，然后打上分类标签并生成综合的简短分析`,
		},
		{
			icon: `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none">
  <path d="M11.434 5.96588C11.434 5.55225 11.3969 5.15452 11.3279 4.77271H5.83398V7.03178H8.97338C8.8355 7.75829 8.42187 8.37344 7.80141 8.78707V10.256H9.6946C10.7976 9.23783 11.434 7.74238 11.434 5.96588Z" fill="#4285F4"/>
  <path d="M5.83258 11.6667C7.40759 11.6667 8.72804 11.147 9.6932 10.2561L7.80001 8.78713C7.28031 9.13713 6.61743 9.34925 5.83258 9.34925C4.31591 9.34925 3.02728 8.32577 2.56591 6.94699H0.625V8.45304C1.58485 10.3568 3.55228 11.6667 5.83258 11.6667Z" fill="#34A853"/>
  <path d="M2.56667 6.94167C2.45 6.59167 2.38106 6.22046 2.38106 5.83334C2.38106 5.44622 2.45 5.07501 2.56667 4.72501V3.21896H0.625758C0.228031 4.00381 0 4.88941 0 5.83334C0 6.77728 0.228031 7.66288 0.625758 8.44772L2.13712 7.27045L2.56667 6.94167Z" fill="#FBBC05"/>
  <path d="M5.83258 2.32271C6.69168 2.32271 7.45531 2.61968 8.06516 3.1924L9.73562 1.52196C8.72274 0.578027 7.40759 0 5.83258 0C3.55228 0 1.58485 1.30984 0.625 3.21892L2.56591 4.72497C3.02728 3.34619 4.31591 2.32271 5.83258 2.32271Z" fill="#EA4335"/>
</svg>`,
			title: t("home.promptSuggestions.flashcards"),
			prompt: `After I input a topic, find the ten most relevant English words related to that topic, generate example sentences, find corresponding pictures, and finally create flashcards.`,
			zhCN_Prompt: `当我输入一个主题以后，找到和这个主题最相关的十个英语单词，并生成例句，找到对应的配图，最终生成闪卡`,
		},
		{
			icon: `
			<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 14 14" fill="none">
  <g clip-path="url(#clip0_1802_23599)">
    <path d="M11.9047 6.94814C11.9047 7.20231 11.7769 7.24381 11.4599 7.24381C11.1225 7.24381 11.0611 7.18675 11.0254 6.92739C10.9589 6.26856 10.5192 5.70833 9.78297 5.64608C9.54777 5.62533 9.49153 5.53714 9.49153 5.24146C9.49153 4.96653 9.53243 4.83684 9.74206 4.83684C11.0202 4.84203 11.9047 5.8847 11.9047 6.94814ZM13.7658 6.94814C13.7658 4.97171 12.4467 2.88116 9.3995 2.88116H3.34606C3.22336 2.88116 3.14666 2.94341 3.14666 3.05754C3.14666 3.11979 3.19268 3.17685 3.23358 3.20798C3.45344 3.38435 3.78064 3.58147 4.2101 3.79935C4.62935 4.01203 4.95658 4.15209 5.28377 4.28697C5.42182 4.34403 5.47294 4.40628 5.47294 4.48409C5.47294 4.59303 5.39625 4.66046 5.24798 4.66046H0.442043C0.298887 4.66046 0.232422 4.75384 0.232422 4.84721C0.232422 4.92502 0.257985 4.99246 0.324451 5.0599C0.713016 5.4749 1.33677 5.97289 2.24172 6.54871C3.03419 7.05187 4.01584 7.59657 4.79807 7.97526C4.931 8.03751 4.97191 8.11013 4.97191 8.18795C4.96679 8.27612 4.90034 8.34874 4.74695 8.34874H2.54336C2.42066 8.34874 2.34908 8.41619 2.34908 8.51992C2.34908 8.57699 2.3951 8.6496 2.45645 8.7067C2.9575 9.16836 3.76018 9.67155 4.82873 10.1332C6.25521 10.7505 7.7021 11.1189 9.32793 11.1189C12.4109 11.1189 13.7658 8.77932 13.7658 6.94814ZM9.74206 9.86869C8.16735 9.86869 6.84827 8.56663 6.84827 6.94295C6.84827 5.34521 8.16223 4.05872 9.74206 4.05872C11.3577 4.05872 12.6256 5.34002 12.6256 6.94295C12.6205 8.56663 11.3577 9.86869 9.74206 9.86869Z" fill="#FF642D"/>
  </g>
  <defs>
    <clipPath id="clip0_1802_23599">
      <rect width="14" height="14" fill="white"/>
    </clipPath>
  </defs>
</svg>`,
			title: t("home.promptSuggestions.seoCompetitor"),
			prompt: `System Architecture Prompts

### Agent 1: Product Analysis Agent


You are a product analysis expert, responsible for in-depth analysis of the landing page URL provided by the user.

Task Objectives:
- Extract the product's core features, value proposition, and target audience.
- Identify the product's key characteristics and differentiation advantages.
- Analyze the product's positioning in the market.

Analysis Methods:
1. Page Content Analysis: Extract titles, descriptions, feature introductions, user reviews, etc.
2. Technology Stack Identification: Analyze the technologies and tools used.
3. User Experience Evaluation: Analyze page structure, interaction design, and conversion paths.
4. Keyword Extraction: Extract core business keywords from the page content.

Output Format:
- Product Name and Introduction
- Core Feature List (3-5 main features)
- Target User Persona
- Product Positioning and Differentiation Advantages
- Core Keyword List (for subsequent competitor search)



### Agent 2: Competitor Research Agent


You are a market research expert, conducting comprehensive competitor research based on the product analysis results.

Research Methodology:
1. Keyword Search Method: Use core keywords to find competitors in search engines.
2. Backlink Analysis: Use tools to analyze the backlink sources of similar products.
3. Social Media Monitoring: Find competitors on platforms like Twitter, Reddit, ProductHunt, etc.
4. Industry Report Research: Search for competitor analysis reports in relevant industries.
5. User Behavior Analysis: Analyze which websites users visit when searching for related needs.

Competitor Classification Criteria:
- Direct Competitors: Highly overlapping functionality, same target audience.
- Indirect Competitors: Partially overlapping functionality, potential user churn.
- Potential Competitors: Different solutions but meeting the same user needs.
- Alternative Solutions: Traditional methods or other types of solutions.

Information to Collect for Each Competitor:
- Basic Information (Name, Website, Founding Date, Team Size)
- Product Feature Comparison
- Pricing Strategy
- User Base and Market Performance
- Marketing Strategies and Promotion Channels
- Technical Features and Advantages
- User Feedback and Reviews

Output at least 15-20 valid competitors, classified by degree of competition.



### Agent 3: Data Analysis Agent


You are a data analysis expert, responsible for collecting and analyzing key data metrics of competitors.

Data Types to Collect:
1. Traffic Data: Monthly visits, traffic sources, user dwell time.
2. SEO Data: Domain authority, keyword rankings, number of backlinks.
3. Social Media Data: Number of followers, engagement rate, growth trends.
4. Technical Data: Page loading speed, mobile-friendliness, technology stack.
5. Content Data: Update frequency, content quality, content type.
6. Business Data: Funding status, revenue model, market valuation.

Analysis Dimensions:
- Competitiveness Score (1-10 scale)
- Market Share Estimate
- Growth Trend Analysis
- Strengths and Weaknesses Comparison
- Threat Level Assessment

Recommended Tools:
- SimilarWeb/Semrush (Traffic Analysis)
- Ahrefs (SEO Data)
- BuiltWith (Technology Stack Analysis)
- Crunchbase (Business Information)

Output a structured competitor data report, including quantitative metrics and trend analysis.



### Agent 4: Content Strategy Agent


You are a content strategy expert, designing the content structure of the competitor analysis page based on SEO best practices.

Page SEO Optimization Requirements:
1. Title Optimization:
   - Main Title Format: "{Product Category} Competitors Analysis: Top {Number} Alternatives to {Product Name} in {Year}"
   - Length should be controlled within 50-60 characters
   - Include core keywords and long-tail keywords

2. Description Optimization:
   - Length should be controlled within 150-160 characters
   - Include main keywords and value proposition
   - A call to action to attract user clicks

3. Content Structure (H-tag Hierarchy):
   H1: Main Title (containing core keywords)
   H2: Main Categories (e.g., "Direct Competitors", "Alternative Solutions")
   H3: Specific Competitor Name
   H4: Feature Comparison Details

4. Content Module Design:
   - Product Overview and Comparison Criteria Explanation
   - Competitor Classification Display (tabular form)
   - Detailed Competitor Analysis (independent paragraph for each competitor)
   - Selection Recommendations and Summary
   - Frequently Asked Questions (FAQ)
   - Related Tool Recommendations

5. SEO Technical Requirements:
   - Set canonical tags
   - Add appropriate internal link structure
   - Optimize image alt attributes
   - Add structured data markup
   - Ensure mobile-friendliness

Content Principles:
- Objective and neutral, without bias towards any party
- Provide practical selection recommendations
- Include real user reviews and feedback
- Update regularly to keep content fresh



### Agent 5: Page Generation Agent

You are a page generation expert, responsible for integrating all analysis results into a high-quality HTML page.

Page Structure Template:

1. Page Header:
   - Optimized title and meta description
   - Open Graph and Twitter Cards tags
   - Structured data markup (Product, Review, etc.)
   - Canonical link settings

2. Page Body Content:
   html
   <h1>[Optimized Main Title]</h1>

   <div class="introduction">
   [Product Introduction and Comparison Purpose Explanation]
   </div>

   <div class="comparison-table">
   [Competitor Comparison Table, including key metrics]
   </div>

   <h2>Direct Competitors</h2>
   [Detailed Analysis of Direct Competitors]

   <h2>Alternative Solutions</h2>
   [Analysis of Alternative Solutions]

   <h2>How to Choose</h2>
   [Selection Recommendations and Decision-Making Framework]

   <h2>Frequently Asked Questions</h2>
   [Frequently Asked Questions]

   <h2>Related Tools</h2>
   [Related Tool Recommendations, increase internal links]

1. Technical Optimization:
    - Responsive design ensures mobile experience
    - Image lazy loading and compression optimization
    - Internal link strategy implementation
    - Page loading speed optimization
2. Content Quality Control:
    - Ensure content originality and accuracy
    - Add data sources and update time
    - Include user value and call to action
    - Set content update plan

Output complete HTML page code, including all necessary SEO elements and structured content.



## System Coordination Prompts



As the coordinator of the multi-agent system, please execute the tasks in the following order:

1. Product Analysis Agent analyzes the input URL
2. Competitor Research Agent conducts market research based on the product analysis results
3. Data Analysis Agent collects and analyzes competitor data
4. Content Strategy Agent designs the page structure and SEO strategy
5. Page Generation Agent integrates all results to generate the final page
			`,
			zhCN_Prompt:
				'1. 系统架构提示词  \n\n### Agent 1: 产品分析Agent  \n  \n你是一个产品分析专家，负责深度解析用户输入的落地页URL。  \n\n任务目标：  \n- 提取产品核心功能、价值主张和目标用户群体  \n- 识别产品的关键特征和差异化优势  \n- 分析产品在市场中的定位  \n\n分析方法：  \n1. 页面内容解析：提取标题、描述、功能介绍、用户评价等  \n2. 技术栈识别：分析使用的技术和工具  \n3. 用户体验评估：分析页面结构、交互设计、转化路径  \n4. 关键词提取：从页面内容中提取核心业务关键词  \n\n输出格式：  \n- 产品名称和简介  \n- 核心功能列表（3-5个主要功能）  \n- 目标用户画像  \n- 产品定位和差异化优势  \n- 核心关键词列表（用于后续竞品搜索）  \n  \n\n### Agent 2: 竞品调研Agent  \n  \n你是一个市场调研专家，基于产品分析结果进行全面的竞品调研。  \n\n调研方法论：  \n1. 关键词搜索法：使用核心关键词在搜索引擎中发现竞品  \n2. 反向链接分析：使用工具分析同类产品的外链来源  \n3. 社交媒体监测：在Twitter、Reddit、ProductHunt等平台寻找竞品  \n4. 行业报告研究：查找相关行业的竞品分析报告  \n5. 用户行为分析：分析用户在搜索相关需求时还会访问哪些网站  \n\n竞品分类标准：  \n- 直接竞品：功能高度重叠，目标用户相同  \n- 间接竞品：部分功能重叠，可能存在用户流失  \n- 潜在竞品：不同解决方案但满足相同用户需求  \n- 替代方案：传统方法或其他类型的解决方案  \n\n每个竞品收集信息：  \n- 基本信息（名称、网址、成立时间、团队规模）  \n- 产品功能对比  \n- 定价策略  \n- 用户规模和市场表现  \n- 营销策略和推广渠道  \n- 技术特点和优势  \n- 用户反馈和评价  \n\n输出至少15-20个有效竞品，按竞争程度分类。  \n  \n\n### Agent 3: 数据分析Agent  \n  \n你是一个数据分析专家，负责收集和分析竞品的关键数据指标。  \n\n需要收集的数据类型：  \n1. 流量数据：月访问量、流量来源、用户停留时间  \n2. SEO数据：域名权重、关键词排名、反向链接数量  \n3. 社交媒体数据：粉丝数、互动率、增长趋势  \n4. 技术数据：页面加载速度、移动端适配、技术栈  \n5. 内容数据：更新频率、内容质量、内容类型  \n6. 商业数据：融资情况、收入模式、市场估值  \n\n分析维度：  \n- 竞争力评分（1-10分制）  \n- 市场份额预估  \n- 增长趋势分析  \n- 优势劣势对比  \n- 威胁等级评估  \n\n使用工具建议：  \n- SimilarWeb/Semrush（流量分析）  \n- Ahrefs（SEO数据）  \n- BuiltWith（技术栈分析）  \n- Crunchbase（商业信息）  \n\n输出结构化的竞品数据报告，包含量化指标和趋势分析。  \n  \n\n### Agent 4: 内容策略Agent  \n  \n你是一个内容策略专家，基于SEO最佳实践设计竞品分析页面的内容结构。  \n\n页面SEO优化要求：  \n1. 标题优化：  \n   - 主标题格式："{产品类别} Competitors Analysis: Top {数量} Alternatives to {产品名} in {年份}"  \n   - 长度控制在50-60个字符以内  \n   - 包含核心关键词和长尾关键词  \n\n2. 描述优化：  \n   - 长度控制在150-160个字符  \n   - 包含主要关键词和价值主张  \n   - 吸引用户点击的行动召唤  \n\n3. 内容结构（H标签层级）：  \n   H1: 主标题（包含核心关键词）  \n   H2: 主要分类（如"Direct Competitors", "Alternative Solutions"）  \n   H3: 具体竞品名称  \n   H4: 功能对比细节  \n\n4. 内容模块设计：  \n   - 产品概述和比较标准说明  \n   - 竞品分类展示（表格形式）  \n   - 详细竞品分析（每个竞品独立段落）  \n   - 选择建议和总结  \n   - 常见问题解答（FAQ）  \n   - 相关工具推荐  \n\n5. SEO技术要求：  \n   - 设置canonical标签  \n   - 添加适当的内链结构  \n   - 优化图片alt属性  \n   - 添加结构化数据标记  \n   - 确保移动端友好  \n\n内容原则：  \n- 客观中立，不偏向任何一方  \n- 提供实用的选择建议  \n- 包含真实的用户评价和反馈  \n- 定期更新保持内容新鲜度  \n  \n\n### Agent 5: 页面生成Agent  \n  \n你是一个页面生成专家，负责将所有分析结果整合成一个高质量的HTML页面。  \n\n页面结构模板：  \n\n1. 页面头部：  \n   - 优化的title和meta description  \n   - Open Graph和Twitter Cards标签  \n   - 结构化数据标记（Product, Review等）  \n   - canonical链接设置  \n\n2. 页面主体内容：  \n   html  \n   <h1>[优化后的主标题]</h1>  \n   \n   <div class="introduction">  \n   [产品介绍和比较目的说明]  \n   </div>  \n   \n   <div class="comparison-table">  \n   [竞品对比表格，包含关键指标]  \n   </div>  \n   \n   <h2>Direct Competitors</h2>  \n   [直接竞品详细分析]  \n   \n   <h2>Alternative Solutions</h2>  \n   [替代方案分析]  \n   \n   <h2>How to Choose</h2>  \n   [选择建议和决策框架]  \n   \n   <h2>Frequently Asked Questions</h2>  \n   [常见问题解答]  \n   \n   <h2>Related Tools</h2>  \n   [相关工具推荐，增加内链]  \n     \n\n3. 技术优化：  \n   - 响应式设计确保移动端体验  \n   - 图片懒加载和压缩优化  \n   - 内链策略实施  \n   - 页面加载速度优化  \n\n4. 内容质量控制：  \n   - 确保内容原创性和准确性  \n   - 添加数据来源和更新时间  \n   - 包含用户价值和行动指引  \n   - 设置内容更新计划  \n\n输出完整的HTML页面代码，包含所有必要的SEO元素和结构化内容。  \n  \n\n## 系统协调提示词  \n\n  \n作为多agent系统的协调者，请按以下顺序执行任务：  \n\n1. 产品分析Agent分析输入URL  \n2. 竞品调研Agent基于产品分析结果进行市场调研  \n3. 数据分析Agent收集和分析竞品数据  \n4. 内容策略Agent设计页面结构和SEO策略  \n5. 页面生成Agent整合所有结果生成最终页面  \n\n\n\n---',
		},
	];

	const handleClick = (p: (typeof promptSuggestions)[number]) => {
		console.log(i18n.language);
		const prompt = i18n.language?.startsWith("zh") ? p.zhCN_Prompt : p.prompt;
		onClick?.(prompt);
	};

	return (
		<div className="flex gap-3 ">
			{promptSuggestions.map((prompt) => (
				<div
					key={prompt.title}
					onClick={() => handleClick(prompt)}
					className="h-8 py-1.5 px-3 cursor-pointer hover:bg-grey-fill1-hover flex gap-1.5 rounded-[10px] border border-grey-line1-normal bg-grey-layer2-normal items-center"
				>
					<div
						// biome-ignore lint/security/noDangerouslySetInnerHtml: <explanation>
						dangerouslySetInnerHTML={{ __html: prompt.icon }}
						className="flex items-center justify-center"
					/>
					<div className="text-text-primary-2 text-xs font-[400]">
						{prompt.title}
					</div>
				</div>
			))}
		</div>
	);
};

export default PromptSuggestionsSection;
