import { theme as antdTheme, ConfigProvider } from "antd";
import type { FC } from "react";
import { useTheme } from "@/hooks/useTheme";

interface Props {
	children: React.ReactNode;
}

const { darkAlgorithm, defaultAlgorithm } = antdTheme;

const AntdThemeConfig: FC<Props> = ({ children }) => {
	const { currentTheme } = useTheme();

	const isDarkMode = currentTheme === "dark";

	const colorPrimary = isDarkMode ? "#7f60ff" : "#6128ff";

	return (
		<ConfigProvider
			theme={{
				algorithm: isDarkMode ? darkAlgorithm : defaultAlgorithm,
				cssVar: {},
				token: {
					paddingXXS: 8,
					colorPrimary,
					colorPrimaryHover: "var(--color-brand-primary-hover)",
					colorPrimaryActive: "var(--color-brand-primary-click)",
					colorLink: "#7450ff",
					colorBgElevated: "var(--color-grey-layer3-normal)",
					// TODO use css var
					colorError: "#e65a5a",
					controlItemBgHover: "var(--color-grey-fill1-hover)",
					controlItemBgActive: "var(--color-brand-primary-focus)",
					zIndexPopupBase: 1000,
					borderRadius: 8,
					borderRadiusSM: 8,
					borderRadiusLG: 12,
					borderRadiusXS: 6,
					fontFamily: "var(--font-dm-sans)",
					boxShadow:
						"0px 0px 0px 1px rgba(255, 255, 255, 0.12), 0px 4px 16px -8px var(--color-shadow-overflow-16), 0px 8px 32px 0px var(--color-shadow-overflow-12), 0px 16px 64px 16px var(--color-shadow-overflow-8)",
					boxShadowSecondary:
						"0px 0px 0px 1px rgba(255, 255, 255, 0.12), 0px 2px 8px -4px var(--color-shadow-overflow-12), 0px 4px 16px 0px var(--color-shadow-overflow-8), 0px 8px 32px 8px var(--color-shadow-overflow-4)",
				},
				components: {
					Button: {
						// 清除按钮阴影
						dangerShadow: "none",
						primaryShadow: "none",
						defaultShadow: "none",
					},
					Menu: {
						itemSelectedColor: "var(--color-brand-primary-normal)",
						itemHoverBg: "var(--color-grey-fill1-hover)",
					},
					Checkbox: {
						borderRadius: 4,
						borderRadiusSM: 4,
						borderRadiusLG: 6,
						borderRadiusXS: 2,
					},
					Modal: {
						borderRadiusLG: 16,
						titleColor: "var(--color-text-primary-1)",
					},
					Notification: {
						borderRadiusLG: 16,
					},
					Input: {
						// 背景
						colorBgContainer: "transparent",
						hoverBg: "transparent",
						activeBg: "transparent",
						// prefix 背景
						addonBg: "var(--color-grey-fill2-normal)",

						// 边框
						colorBorder: "var(--color-grey-line2-normal)",
						hoverBorderColor: "var(--color-grey-line2-normal)",
						activeBorderColor: "var(--color-brand-secondary-normal)",
						colorError: "var(--color-error-normal)",
						colorErrorBorder: "var(--color-error-normal)",

						// 阴影
						activeShadow: "0 0 0 3px var(--color-focus-primary-1)",
						errorActiveShadow: "0 0 0 3px var(--color-focus-error-1)",

						// 文字
						colorText: "var(--color-text-primary-1)",
						colorTextPlaceholder: "var(--color-text-primary-5)",
						// 字数统计文本颜色
						colorTextDescription: "var(--color-text-primary-4)",
					},
					Tooltip: {
						borderRadiusXS: 1,
						colorBgSpotlight: "var(--color-grey-layer3-reserve)",
						colorText: "var(--color-text-primary-1)",
					},
					Dropdown: {
						borderRadiusXS: 2,
						borderRadiusLG: 16,
						controlItemBgHover: "var(--color-grey-fill1-hover)",
						controlItemBgActive: "var(--color-brand-primary-focus)",
						paddingXXS: 8,
					},
					Drawer: {
						colorBgElevated: "var(--color-grey-layer2-normal)",
						borderRadiusLG: 12,
					},
					Radio: {
						// 1px border 在 150% 渲染分辨率下为 0.6667px 下 使用此颜色会导致清晰度不够
						// colorBorder: 'var(--color-grey-line2-normal)',
						// colorBgContainer: 'transparent',
						colorPrimary: "var(--color-brand-primary-normal)",
					},
					Select: {
						selectorBg: "transparent",
						paddingXXS: 8,
					},
					Switch: {
						colorPrimary: "var(--color-brand-primary-normal)",
						// 关闭时 背景色
						colorTextQuaternary: "var(--color-grey-line2-normal)",
						// 关闭时 hover 背景色
						colorTextTertiary: "var(--color-grey-line2-hover)",
					},
					Popover: {
						borderRadiusXS: 2,
						borderRadiusLG: 16,
						// colorBgContainer: 'var(--color-grey-layer1-normal)',
					},
					Image: {
						colorBgMask: "rgba(0, 0, 0, 0.65)",
					},
				},
			}}
		>
			{children}
		</ConfigProvider>
	);
};

export default AntdThemeConfig;
