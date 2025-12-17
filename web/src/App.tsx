import NiceModal from "@ebay/nice-modal-react";
import { QueryClientProvider } from "@tanstack/react-query";
import { App as AntApp } from "antd";
import { RouterProvider } from "react-router";
import AntdThemeProvider from "@/components/provider/AntdThemeProvider";
import { ThemeProvider } from "@/components/provider/ThemeProvider";
import { queryClient } from "@/lib/queryClient";
import router from "@/router";

function App() {
	return (
		<QueryClientProvider client={queryClient}>
			<ThemeProvider>
				<AntdThemeProvider>
					<AntApp className="h-full">
						<NiceModal.Provider>
							<RouterProvider router={router} />
						</NiceModal.Provider>
					</AntApp>
				</AntdThemeProvider>
			</ThemeProvider>
		</QueryClientProvider>
	);
}

export default App;
