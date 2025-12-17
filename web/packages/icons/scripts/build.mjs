import { transform } from '@svgr/core';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import svgrConfig from '../svgr.config.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const SVG_DIR = path.join(__dirname, '../icons');
const OUTPUT_DIR = path.join(__dirname, '../src/icons');

// console.log('开始构建');

/* eslint-disable import/prefer-default-export */
/**
 * Converts string to CamelCase
 *
 * @param {string} string
 * @returns {string} A camelized string
 */
export const toCamelCase = (string) =>
  string.replace(/^([A-Z])|[\s-_]+(\w)/g, (match, p1, p2) =>
    p2 ? p2.toUpperCase() : p1.toLowerCase(),
  );

/**
 * Converts string to PascalCase
 *
 * @param {string} string
 * @returns {string} A pascalized string
 */
export const toPascalCase = (string) => {
  const camelCase = toCamelCase(string);

  return camelCase.charAt(0).toUpperCase() + camelCase.slice(1);
};

async function generateIconsIndex(iconNames) {
  const exportStatements = iconNames
    .map((name) => `export { default as ${name} } from './${name}';`)
    .join('\n');

  await fs.writeFile(
    path.join(OUTPUT_DIR, 'index.ts'),
    exportStatements,
    'utf8',
  );
}

const template = (variables, { tpl }) => {
  // console.log('variables', JSON.stringify(variables.jsx, null, 2));
  const componentName = variables.componentName;
  const baseComponentName = `${componentName}Base`;

  return tpl`
${variables.imports};
import type { IconProps } from '../type';

${variables.interfaces};

const ${baseComponentName} = ({
  color = 'currentColor', 
  size = '1em',
  ...props
}: IconProps) => {
  const uniqueID = React.useId();
  const componentName = "${variables.componentName}";

  return (
    ${variables.jsx}
  );
};

__annotation__
const ${componentName} = React.memo(${baseComponentName});

export default ${componentName};
`;
};

function replaceTemplateStringQuotes(tsx) {
  // 使用正则表达式查找含有 ${} 的双引号字符串
  return tsx.replace(/"([^"]*\$\{[^"]*}[^"]*)"/g, '{`$1`}');
}

function parseSvg(svgCode) {
  const svgMatch = svgCode.match(/<svg([^>]*)>([\s\S]*)<\/svg>/i);

  if (!svgMatch) {
    throw new Error('Invalid SVG code');
  }

  const [_, attributesStr, content] = svgMatch;

  const attributes = {};
  const attrRegex = /(\w+)=["']([^"']*)["']/g;
  let match;

  while ((match = attrRegex.exec(attributesStr)) !== null) {
    attributes[match[1]] = match[2];
  }

  return {
    attributes,
    content,

    toString() {
      let attrsString = Object.entries(this.attributes)
        .map(([key, value]) => `${key}="${value}"`)
        .join(' ');

      if (attrsString) attrsString = ' ' + attrsString;

      return `<svg${attrsString}>${this.content}</svg>`;
    },

    setAttribute(name, value) {
      this.attributes[name] = value;
      return this;
    },

    removeAttribute(name) {
      delete this.attributes[name];
      return this;
    },

    setContent(newContent) {
      this.content = newContent;
      return this;
    },

    stringify() {
      const svgCode = this.toString();

      const minifiedSvg = svgCode
        .replace(/>\s+</g, '><')
        .replace(/\s{2,}/g, ' ')
        .replace(/[\r\n\t]/g, '')
        .trim();

      const base64 = btoa(minifiedSvg);

      return {
        data: `data:image/svg+xml;base64,${base64}`,
        base64,
        minifiedSvg,
      };
    },
  };
}

async function buildIcons() {
  try {
    // 确保输出目录存在
    await fs.mkdir(OUTPUT_DIR, { recursive: true });

    // 读取所有SVG文件
    const files = await fs.readdir(SVG_DIR);
    const svgFiles = files.filter((file) => file.endsWith('.svg'));

    const iconNames = [];

    // 转换每个SVG文件
    for (const file of svgFiles) {
      const svgPath = path.join(SVG_DIR, file);
      const svgCode = await fs.readFile(svgPath, 'utf8');

      // 生成组件名 (PascalCase)
      const componentName = toPascalCase(file.replace(/\.svg$/, ''));

      iconNames.push(componentName);

      // 使用SVGR转换SVG为React组件
      let jsCode = await transform(
        svgCode,
        {
          ...svgrConfig,
          template,
        },
        {
          componentName,
        },
      );

      // console.log('jsCode', jsCode);
      jsCode = jsCode.replaceAll(
        '__annotation__;',
        `/**
 * @name ${componentName}
 * 
 * @preview ![${componentName}](${
   parseSvg(svgCode)
     .setAttribute('width', '32')
     .setAttribute('height', '32')
     .setAttribute('style', 'background-color: white;')
     .stringify().data
 })
 */`,
      );

      // 转换为ESM模块
      let esmCode = jsCode.replace('module.exports =', 'export default');

      // 替换 '{{componentName}}'
      // esmCode = esmCode.replaceAll('{{componentName}}', componentName);

      esmCode = replaceTemplateStringQuotes(esmCode);

      // 写入.tsx文件
      await fs.writeFile(
        path.join(OUTPUT_DIR, `${componentName}.tsx`),
        esmCode,
        'utf8',
      );
    }

    // 生成索引文件
    await generateIconsIndex(iconNames);

    console.log(`已成功生成 ${svgFiles.length} 个图标组件!`);
  } catch (error) {
    console.error('构建图标时出错:', error);
    console.error('Error details:', error.stack);
    process.exit(1); // Exit with error code to fail the build
  }
}

buildIcons();
