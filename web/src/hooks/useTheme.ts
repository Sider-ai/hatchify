import { useContext } from "react";
import {
	ThemeProviderContext,
	type ThemeProviderState,
} from "@/components/provider/ThemeProvider";

export const useTheme = () => {
	const context = useContext<ThemeProviderState>(ThemeProviderContext);

	if (context === undefined)
		throw new Error("useTheme must be used within a ThemeProvider");

	return context;
};
