import JSZip from "jszip";

export const zip = new JSZip();

export interface ZipFile {
	name: string;
	content: string;
	path: string;
	isDirectory: boolean;
	extension: string;
}

export interface ProjectStructure {
	files: ZipFile[];
	directories: string[];
	htmlFiles: ZipFile[];
	cssFiles: ZipFile[];
	jsFiles: ZipFile[];
	imageFiles: ZipFile[];
	otherFiles: ZipFile[];
}

/**
 * 从 URL 下载并解析 ZIP 文件
 */
export async function downloadAndExtractZip(
	url: string,
): Promise<Record<string, string>> {
	try {
		// 下载 ZIP 文件
		const response = await fetch(url);
		if (!response.ok) {
			throw new Error(`Failed to download ZIP: ${response.statusText}`);
		}

		const arrayBuffer = await response.arrayBuffer();
		const zip = new JSZip();
		const zipContent = await zip.loadAsync(arrayBuffer);

		console.log(zipContent);

		const filesJson: Record<string, string> = {};
		for (const [path, zipEntry] of Object.entries(zipContent.files)) {
			const content = await zipEntry.async("string");
			filesJson[path] = content;
		}

		return filesJson;
	} catch (error) {
		console.error(error);
		throw error;
	}
}

/**
 * 查找入口 HTML 文件
 */
export function findEntryPoint(structure: ProjectStructure): ZipFile | null {
	// 优先查找 index.html
	let entryPoint = structure.htmlFiles.find(
		(f) => f.name.toLowerCase() === "index.html",
	);

	// 如果没有 index.html，查找根目录下的任何 HTML 文件
	if (!entryPoint) {
		entryPoint = structure.htmlFiles.find((f) => !f.path.includes("/"));
	}

	// 如果还没有，返回第一个 HTML 文件
	if (!entryPoint && structure.htmlFiles.length > 0) {
		entryPoint = structure.htmlFiles[0];
	}

	return entryPoint || null;
}

/**
 * 创建文件的 Blob URL（用于预览图片、CSS、JS 等）
 */
export function createBlobUrl(file: ZipFile): string {
	const mimeTypes: Record<string, string> = {
		html: "text/html",
		css: "text/css",
		js: "application/javascript",
		json: "application/json",
		txt: "text/plain",
		png: "image/png",
		jpg: "image/jpeg",
		jpeg: "image/jpeg",
		gif: "image/gif",
		svg: "image/svg+xml",
		webp: "image/webp",
	};

	const mimeType = mimeTypes[file.extension] || "text/plain";
	const blob = new Blob([file.content], { type: mimeType });
	return URL.createObjectURL(blob);
}

/**
 * 处理 HTML 文件中的相对路径，替换为 Blob URLs
 */
export function processHtmlContent(
	htmlFile: ZipFile,
	structure: ProjectStructure,
): string {
	let htmlContent = htmlFile.content;
	const baseDir = htmlFile.path.substring(0, htmlFile.path.lastIndexOf("/"));

	// 创建所有文件的 Blob URL 映射
	const blobUrls = new Map<string, string>();
	structure.files.forEach((file) => {
		if (file !== htmlFile) {
			blobUrls.set(file.path, createBlobUrl(file));
		}
	});

	// 替换 CSS 链接
	htmlContent = htmlContent.replace(
		/<link[^>]+href=['"]([^'"]+)['"][^>]*>/gi,
		(match, href) => {
			const resolvedPath = resolvePath(baseDir, href);
			const blobUrl = blobUrls.get(resolvedPath);
			return blobUrl ? match.replace(href, blobUrl) : match;
		},
	);

	// 替换 JavaScript 脚本
	htmlContent = htmlContent.replace(
		/<script[^>]+src=['"]([^'"]+)['"][^>]*>/gi,
		(match, src) => {
			const resolvedPath = resolvePath(baseDir, src);
			const blobUrl = blobUrls.get(resolvedPath);
			return blobUrl ? match.replace(src, blobUrl) : match;
		},
	);

	// 替换图片链接
	htmlContent = htmlContent.replace(
		/<img[^>]+src=['"]([^'"]+)['"][^>]*>/gi,
		(match, src) => {
			const resolvedPath = resolvePath(baseDir, src);
			const blobUrl = blobUrls.get(resolvedPath);
			return blobUrl ? match.replace(src, blobUrl) : match;
		},
	);

	// 替换 CSS 中的 background-image 和其他 url() 引用
	structure.cssFiles.forEach((cssFile) => {
		const cssPath = cssFile.path;
		const cssBlobUrl = blobUrls.get(cssPath);
		if (cssBlobUrl) {
			// 更新 CSS 文件内容中的相对路径
			let cssContent = cssFile.content;
			cssContent = cssContent.replace(
				/url\(['"]?([^'")\s]+)['"]?\)/gi,
				(match, url) => {
					if (url.startsWith("http") || url.startsWith("data:")) {
						return match;
					}
					const cssBaseDir = cssPath.substring(0, cssPath.lastIndexOf("/"));
					const resolvedPath = resolvePath(cssBaseDir, url);
					const imageBlobUrl = blobUrls.get(resolvedPath);
					return imageBlobUrl ? `url('${imageBlobUrl}')` : match;
				},
			);

			// 重新创建 CSS Blob URL
			const updatedBlob = new Blob([cssContent], { type: "text/css" });
			const updatedBlobUrl = URL.createObjectURL(updatedBlob);
			blobUrls.set(cssPath, updatedBlobUrl);

			// 更新 HTML 中的 CSS 链接
			htmlContent = htmlContent.replace(cssBlobUrl, updatedBlobUrl);
		}
	});

	return htmlContent;
}

/**
 * 解析相对路径
 */
function resolvePath(basePath: string, relativePath: string): string {
	if (relativePath.startsWith("/")) {
		return relativePath.substring(1);
	}

	if (basePath === "") {
		return relativePath;
	}

	const baseSegments = basePath.split("/");
	const relativeSegments = relativePath.split("/");

	for (const segment of relativeSegments) {
		if (segment === "..") {
			baseSegments.pop();
		} else if (segment !== ".") {
			baseSegments.push(segment);
		}
	}

	return baseSegments.join("/");
}

/**
 * 清理所有创建的 Blob URLs（防止内存泄漏）
 */
export function cleanupBlobUrls(urls: string[]): void {
	urls.forEach((url) => {
		if (url.startsWith("blob:")) {
			URL.revokeObjectURL(url);
		}
	});
}
