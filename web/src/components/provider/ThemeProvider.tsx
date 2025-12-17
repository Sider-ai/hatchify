import { createContext, useEffect, useMemo, useState } from "react";

export type Theme = "dark" | "light" | "system";

interface ThemeProviderProps {
	children: React.ReactNode;
	defaultTheme?: Theme;
	storageKey?: string;
}

export interface ThemeProviderState {
	theme: Theme;
	setTheme: (theme: Theme) => void;
	currentTheme: Theme;
}

const initialState: ThemeProviderState = {
	theme: "system",
	setTheme: () => null,
	currentTheme: "system",
};

export const ThemeProviderContext =
	createContext<ThemeProviderState>(initialState);

export function ThemeProvider({
	children,
	defaultTheme = "system",
	storageKey = "__ui-theme__",
	...props
}: ThemeProviderProps) {
	const [theme, setTheme] = useState<Theme>(
		() => (localStorage.getItem(storageKey) as Theme) || defaultTheme,
	);
	const [currentTheme, setCurrentTheme] = useState<Theme>(theme);

	useEffect(() => {
		const root = window.document.documentElement;

		root.classList.remove("light", "dark");

		const applyTheme = () => {
			if (theme === "system") {
				const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
					.matches
					? "dark"
					: "light";
				root.classList.remove("light", "dark");
				root.classList.add(systemTheme);
				setCurrentTheme(systemTheme);
			} else {
				root.classList.remove("light", "dark");
				root.classList.add(theme);
				setCurrentTheme(theme);
			}
		};

		// 初始应用主题
		applyTheme();

		// 监听系统主题变化（仅在使用 system 主题时）
		if (theme === "system") {
			const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
			const handleChange = () => {
				applyTheme();
			};

			// 现代浏览器使用 addEventListener
			if (mediaQuery.addEventListener) {
				mediaQuery.addEventListener("change", handleChange);
				return () => mediaQuery.removeEventListener("change", handleChange);
			}
			// 旧浏览器回退
			else if (mediaQuery.addListener) {
				mediaQuery.addListener(handleChange);
				return () => mediaQuery.removeListener(handleChange);
			}
		}
	}, [theme]);

	useEffect(() => {
		const handleStorageChange = (event: StorageEvent) => {
			if (event.key === storageKey && event.newValue) {
				setTheme(event.newValue as Theme);
			}
		};

		window.addEventListener("storage", handleStorageChange);

		return () => {
			window.removeEventListener("storage", handleStorageChange);
		};
	}, [storageKey]);

	const value = useMemo(
		() => ({
			theme,
			setTheme: (theme: Theme) => {
				localStorage.setItem(storageKey, theme);
				setTheme(theme);
			},
			currentTheme,
		}),
		[storageKey, theme, currentTheme],
	);

	return (
		<ThemeProviderContext.Provider {...props} value={value}>
			{children}
		</ThemeProviderContext.Provider>
	);
}
