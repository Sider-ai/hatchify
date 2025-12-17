import { icons } from "@icons/index";
import prettier from "prettier";
import parserHtml from "prettier/plugins/html";
import { useEffect, useMemo, useRef, useState } from "react";
import { type INode, parseSync, stringify } from "svgson";
import IconRender from "./IconRender";
import "./index.css";
import toast from "./toast";

const copyText = (text: string) => {
	navigator.clipboard.writeText(text);
	toast.success("复制成功");
};

enum Mode {
	Search = "search",
	Add = "add",
}

export default function Page() {
	const [mode, setMode] = useState<Mode>(Mode.Search);
	const pathname = window.location.pathname;

	useEffect(() => {
		if (pathname === "/") {
			setMode(Mode.Search);
		} else if (pathname === "/add") {
			setMode(Mode.Add);
		}
	}, [pathname]);

	return (
		<div className="page">
			<div className="sidebar">
				<div
					onClick={() => {
						setMode(Mode.Search);
						window.history.pushState({}, "", "/");
					}}
				>
					搜索图标
				</div>
				<div
					onClick={() => {
						setMode(Mode.Add);
						window.history.pushState({}, "", "/add");
					}}
				>
					添加图标
				</div>
			</div>
			<div className="container">
				{mode === Mode.Search && <Search />}
				{mode === Mode.Add && <Add />}
			</div>
		</div>
	);
}

function Search() {
	const [search, setSearch] = useState("");
	const ref = useRef<HTMLDivElement>(null);

	const [iconColor, setIconColor] = useState("#000000");
	const [theme, setTheme] = useState("light");

	// 新增防抖处理
	const [debouncedSearch, setDebouncedSearch] = useState("");

	// 防抖效果
	useEffect(() => {
		const timer = setTimeout(() => {
			setDebouncedSearch(search);
		}, 300);

		return () => {
			clearTimeout(timer);
		};
	}, [search]);

	// 模糊搜索逻辑
	const fuzzyMatch = (text: string, pattern: string): number => {
		if (!pattern) return 1; // 空搜索返回最高匹配度

		// 转为小写进行不区分大小写的匹配
		text = text.toLowerCase();
		pattern = pattern.toLowerCase();

		// 移除输入文本中的空格和'-'
		text = text
			.replaceAll(/\s+/g, "")
			.replaceAll(/-/g, "")
			.replaceAll("_", "")
			.replaceAll(".", "");
		pattern = pattern
			.replaceAll(/\s+/g, "")
			.replaceAll(/-/g, "")
			.replaceAll("_", "")
			.replaceAll(".", "");

		// 完全包含的情况优先级最高
		if (text.includes(pattern)) return 1;

		// 按字符顺序匹配
		let score = 0;
		let patternIdx = 0;
		let consecutiveMatches = 0;

		for (let i = 0; i < text.length && patternIdx < pattern.length; i++) {
			if (text[i] === pattern[patternIdx]) {
				// 连续匹配会增加分数
				consecutiveMatches++;
				score += consecutiveMatches + 0.5;
				patternIdx++;
			} else {
				consecutiveMatches = 0;
			}
		}

		// 没有匹配完所有字符
		if (patternIdx < pattern.length) {
			return 0;
		}

		// 根据匹配字符数和文本长度计算相似度得分
		return score / (text.length * 2);
	};

	// 对图标进行模糊搜索并按匹配度排序
	const filteredIcons = useMemo(() => {
		if (!debouncedSearch) {
			return Object.entries(icons).map(([key, Icon]) => ({
				key,
				Icon,
				score: 1,
			}));
		}

		return Object.entries(icons)
			.map(([key, Icon]) => {
				const score = fuzzyMatch(key, debouncedSearch);
				return { key, Icon, score };
			})
			.filter((item) => item.score > 0)
			.sort((a, b) => b.score - a.score);
	}, [debouncedSearch]);

	return (
		<div
			ref={ref}
			style={{
				display: "flex",
				flexDirection: "column",
				gap: 12,
				overflow: "hidden",
			}}
		>
			<div style={{ display: "flex", justifyContent: "space-between" }}>
				<div className="title">图标总览（{Object.keys(icons).length}）</div>
				<div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
					<div style={{ display: "flex", alignItems: "center", gap: 4 }}>
						<div>颜色</div>
						<input
							type="color"
							value={iconColor}
							onChange={(e) => setIconColor(e.target.value)}
							style={{ border: "none", backgroundColor: "transparent" }}
						/>
					</div>
					<div style={{ display: "flex", alignItems: "center", gap: 4 }}>
						<div>背景</div>
						<select value={theme} onChange={(e) => setTheme(e.target.value)}>
							<option value="light">亮色</option>
							<option value="dark">暗色</option>
						</select>
					</div>
				</div>
			</div>
			<div className="tips">
				1. 点击图标复制 Icon 的组件代码
				<br />
				2. 点击图标下方文本复制对应的内容
			</div>
			<div className="search">
				<input
					autoFocus
					value={search}
					onChange={(e) => setSearch(e.target.value)}
					placeholder="输入关键字搜索图标..."
				/>
				{debouncedSearch && (
					<div style={{ fontSize: "12px", color: "#666" }}>
						{`找到 ${filteredIcons.length} 个图标`}
					</div>
				)}
			</div>
			<div style={{ flex: 1, overflowY: "auto" }}>
				<div
					style={{
						display: "flex",
						flexWrap: "wrap",
						gap: "16px",
						justifyContent: "center",
					}}
				>
					{filteredIcons.map(({ key, Icon, score }) => (
						<div
							key={key}
							style={{
								cursor: "pointer",
								fontSize: 10,
								width: `100px`,
								display: "flex",
								flexDirection: "column",
								alignItems: "center",
								justifyContent: "center",
								// 高亮显示匹配度高的结果
								opacity: debouncedSearch ? 0.5 + score * 0.5 : 1,
							}}
						>
							<div
								className="icon-wrapper"
								style={{
									color: iconColor,
									backgroundColor: theme === "light" ? "#f6f6f6" : "#1a1a1a",
									borderRadius: 12,
									padding: 12,
								}}
							>
								<Icon size={48} onClick={() => copyText(`<${key} />`)} />
							</div>
							<div onClick={() => copyText(key)} className="icon-name">
								{key}
							</div>
						</div>
					))}

					{filteredIcons.length === 0 && debouncedSearch && (
						<div
							style={{
								width: "100%",
								textAlign: "center",
								padding: "40px 0",
								color: "#999",
							}}
						>
							未找到匹配的图标
						</div>
					)}
				</div>
			</div>
		</div>
	);
}

function Add() {
	const [svgStr, setSvgStr] = useState("");
	const [processedSvgStr, setProcessedSvgStr] = useState("");
	const [autoConvert, setAutoConvert] = useState(true);
	const [name, setName] = useState("");
	const [isColorful, setIsColorful] = useState(false);

	const [config, setConfig] = useState({
		download: {
			clearSvgStr: true,
			clearProcessedSvgStr: true,
			clearName: true,
		},
	});

	const [color, setColor] = useState("#66ccff");

	useEffect(() => {
		if (autoConvert) {
			parseSvgStrToIconNode(svgStr);
		}
	}, [svgStr, autoConvert, isColorful]);

	const parseSvgStrToIconNode = async (str: string) => {
		const iconNode = parseSync(str);
		iconNode.attributes.fill = "currentColor";
		// 递归删除所有 fill 和 fill-opacity 属性
		const deleteFill = (node: INode, deep: number) => {
			const keepFill =
				isColorful || node.attributes.keepFill === "1" || deep === 1;

			if (node.attributes.keepFill) {
				delete node.attributes.keepFill;
			}
			if (!keepFill) {
				if (node.attributes.fill) {
					delete node.attributes.fill;
				}
				if (node.attributes["fill-opacity"]) {
					delete node.attributes["fill-opacity"];
				}
			}

			node.children.forEach((child) => {
				deleteFill(child, deep + 1);
			});
		};
		deleteFill(iconNode, 1);
		const processed = stringify(iconNode);
		handleProcessedSvgStr(processed);
	};

	const handleProcessedSvgStr = async (str: string) => {
		const processed = await formatSvgStr(str);
		setProcessedSvgStr(processed);
	};

	const formatSvgStr = async (str: string) => {
		const processed = await prettier.format(str, {
			parser: "html",
			plugins: [parserHtml],
			printWidth: 80,
		});
		return processed;
	};

	const downloadSvg = () => {
		const blob = new Blob([processedSvgStr], {
			type: "image/svg+xml",
		});
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		const fileName =
			name
				.split("-")
				.map((name) => name.trim())
				.filter((name) => {
					// 不能包含中文
					return Boolean(name) && !/[\u4e00-\u9fa5]/.test(name);
				})
				.join("-") || "icon";
		a.download = `${fileName}.svg`;
		a.click();
		URL.revokeObjectURL(url);
		if (config.download.clearSvgStr) {
			setSvgStr("");
		}
		if (config.download.clearProcessedSvgStr) {
			setProcessedSvgStr("");
		}
		if (config.download.clearName) {
			setName("");
		}
	};

	const handleIsColorful = (e: React.ChangeEvent<HTMLInputElement>) => {
		setIsColorful(e.target.checked);
	};

	return (
		<div className="f-x-center" style={{ width: "100%" }}>
			<div className="title">添加图标</div>
			<div className="tips" style={{ marginBottom: 12 }}>
				1. 从 Figma 中导出 svg 代码并粘贴到左边输入框中
				<br />
				2. 对于多色图标，可以添加 keepFill=&quot;1&quot; 属性来保持当前部分的
				fill 和 fill-opacity 属性，最外层的不用添加，会默认保留
				<br />
				3. 点击转化按钮，自动将最外层的 fill 更改为 currentColor，内部没有
				keepFill=&quot;1&quot; 的会被移除 fill 和 fill-opacity 属性
				<br />
				4. 可以通过左右两侧文本框下面的图标预览来检查自动处理后是否正确
			</div>
			<div style={{ marginBottom: 16 }}>
				快速复制：
				<div
					style={{
						display: "inline-block",
						padding: "4px 8px",
						backgroundColor: "#f0f0f0",
						borderRadius: 4,
						cursor: "pointer",
						marginLeft: 4,
					}}
					onClick={() => copyText('keepFill="1"')}
				>
					keepFill=&quot;1&quot;
				</div>
			</div>
			<div className="add-container">
				<div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
					<textarea
						value={svgStr}
						style={{
							width: "100%",
							padding: 12,
							boxSizing: "border-box",
							flex: 1,
						}}
						placeholder="请输入图标 svg 代码"
						onChange={(e) => setSvgStr(e.target.value)}
					/>
					<div>
						<button
							style={{ padding: "4px 8px", height: 32, margin: "12px 0" }}
							onClick={async () => {
								const processedSvgStr = await formatSvgStr(svgStr);
								setSvgStr(processedSvgStr);
							}}
						>
							格式化代码
						</button>
					</div>
					<IconRender svgStr={svgStr} size={48} />
				</div>
				<div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
					<button
						style={{ padding: "4px 8px" }}
						onClick={() => parseSvgStrToIconNode(svgStr)}
					>
						转化
					</button>
					<div style={{ display: "flex", alignItems: "center", gap: 4 }}>
						<input
							id="auto-convert"
							type="checkbox"
							style={{ padding: "4px 8px" }}
							checked={autoConvert}
							onChange={(e) => setAutoConvert(e.target.checked)}
						/>
						<label htmlFor="auto-convert" style={{ fontSize: 14 }}>
							自动转化
						</label>
					</div>
					<div style={{ display: "flex", alignItems: "center", gap: 4 }}>
						<input
							id="is-colorful"
							type="checkbox"
							style={{ padding: "4px 8px" }}
							checked={isColorful}
							onChange={handleIsColorful}
						/>
						<label htmlFor="is-colorful" style={{ fontSize: 14 }}>
							多色图标
						</label>
					</div>
					<div>下载后：</div>
					<div style={{ display: "flex", alignItems: "center", gap: 4 }}>
						<input
							id="clear-svg-str"
							type="checkbox"
							style={{ padding: "4px 8px" }}
							checked={config.download.clearSvgStr}
							onChange={() =>
								setConfig({
									...config,
									download: {
										...config.download,
										clearSvgStr: !config.download.clearSvgStr,
									},
								})
							}
						/>
						<label htmlFor="is-colorful" style={{ fontSize: 14 }}>
							删除 svg 代码
						</label>
					</div>
					<div style={{ display: "flex", alignItems: "center", gap: 4 }}>
						<input
							id="clear-processed-svg-str"
							type="checkbox"
							style={{ padding: "4px 8px" }}
							checked={config.download.clearProcessedSvgStr}
							onChange={() =>
								setConfig({
									...config,
									download: {
										...config.download,
										clearProcessedSvgStr: !config.download.clearProcessedSvgStr,
									},
								})
							}
						/>
						<label htmlFor="clear-processed-svg-str" style={{ fontSize: 14 }}>
							删除处理后的 svg 代码
						</label>
					</div>
					<div style={{ display: "flex", alignItems: "center", gap: 4 }}>
						<input
							id="clear-name"
							type="checkbox"
							style={{ padding: "4px 8px" }}
							checked={config.download.clearName}
							onChange={() =>
								setConfig({
									...config,
									download: {
										...config.download,
										clearName: !config.download.clearName,
									},
								})
							}
						/>
						<label htmlFor="clear-name" style={{ fontSize: 14 }}>
							删除文件名
						</label>
					</div>
				</div>
				<div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
					<textarea
						value={processedSvgStr}
						onChange={(e) => setProcessedSvgStr(e.target.value)}
						style={{
							width: "100%",
							padding: 12,
							boxSizing: "border-box",
							flex: 1,
						}}
						placeholder="自动处理后的 svg 代码"
					/>
					<div>
						<div>
							<div
								style={{
									margin: "12px 0",
									height: 32,
									display: "flex",
									gap: 12,
								}}
							>
								<div
									style={{
										display: "flex",
										alignItems: "center",
										gap: 4,
									}}
								>
									<input
										type="text"
										style={{ padding: "4px 8px" }}
										value={name}
										onChange={(e) => setName(e.target.value)}
										placeholder="请输入图标文件名"
										onKeyDown={(e) => {
											if (e.key === "Enter") {
												downloadSvg();
											}
										}}
									/>
									<div>.svg</div>
								</div>

								<div style={{ display: "flex", gap: 8 }}>
									<button
										style={{ padding: "4px 8px", flexShrink: 0 }}
										onClick={downloadSvg}
									>
										下载
									</button>
									<button
										style={{ padding: "4px 8px", flexShrink: 0 }}
										onClick={() => copyText(processedSvgStr)}
									>
										复制
									</button>
								</div>
							</div>
							<div
								style={{
									margin: "12px 0",
									height: 32,
									display: "flex",
									gap: 12,
								}}
							>
								{/* 添加颜色输入 */}
								<input
									type="text"
									style={{ padding: "4px 8px" }}
									value={color}
									onChange={(e) => setColor(e.target.value)}
								/>
								<input
									type="color"
									style={{ height: "100%", padding: "0 4px" }}
									value={color}
									onChange={(e) => setColor(e.target.value)}
								/>
							</div>
							{/* 颜色预览 */}
							<div style={{ color: color }}>
								<IconRender svgStr={processedSvgStr} size={48} />
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}
