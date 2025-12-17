export default {
  icon: true,
  typescript: true,
  prettier: false,
  memo: false,
  plugins: ['@svgr/plugin-svgo', '@svgr/plugin-jsx'],
  svgoConfig: {
    plugins: [
      {
        name: 'preset-default',
        params: {
          overrides: {
            removeViewBox: false,
          },
        },
      },
      {
        name: 'prefixIds',
        params: {
          delim: '',
          prefix: 'icon-${componentName}-${uniqueID}-',
        },
      },
    ],
  },
  svgProps: {
    fill: '{color}', // SVGR 会将其转换为 fill={color}
    width: '{size}', // 这里的表达式要放在 {} 内部
    height: '{size}',
  },
};
