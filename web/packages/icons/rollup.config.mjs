import dts from 'rollup-plugin-dts';
import esbuild from 'rollup-plugin-esbuild';
import preserveDirectives from 'rollup-plugin-preserve-directives';

/**
 * @import { RollupOptions } from "rollup"
 */

/**
 * @type {RollupOptions[]}
 */
const config = [
  {
    input: 'src/index.ts',
    output: {
      format: 'es',
      file: 'dist/index.d.ts',
    },
    plugins: [dts()],
    external: ['react', /^react\//],
  },
  {
    input: 'src/index.ts',
    output: {
      sourcemap: true,
      format: 'esm',
      dir: 'dist/esm',
      preserveModules: true,
      preserveModulesRoot: 'src',
      globals: {
        react: 'react',
        'react/jsx-runtime': 'react/jsx-runtime',
      },
    },
    plugins: [
      esbuild({
        jsx: 'automatic',
        tsconfig: './tsconfig.json',
      }),
      preserveDirectives({
        // 修正为指令名称列表
        include: ['use client', 'use strict', 'use client'],
        suppressPreserveModulesWarning: true,
      }),
    ],
    // 使用正则表达式匹配所有 React 相关的包
    external: ['react', /^react\//],
  },
];

export default config;
