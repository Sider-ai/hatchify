import path from "node:path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv, type PluginOption } from "vite";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), "");
	const apiTarget = env.VITE_API_TARGET || "http://localhost:8000";

	return {
		plugins: [react(), tailwindcss() as PluginOption],
		resolve: {
			alias: {
				"@": path.resolve(__dirname, "src"),
			},
		},
		server: {
			proxy: {
				"/api": {
					target: apiTarget,
					changeOrigin: true,
					secure: false,
					rewrite: (path) => path,
				},
			},
		},
	};
});
