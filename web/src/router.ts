import { lazy } from "react";
import { createBrowserRouter } from "react-router";
import StudioPage from "@/app/studio/Studio";

const router = createBrowserRouter([
	{
		path: "/",
		Component: lazy(() => import("@/app/home/Home")),
	},
	{
		path: "/studio/:id",
		Component: StudioPage,
	},
	{
		path: "/settings",
		Component: lazy(() => import("@/app/settings/Settings")),
	},
]);
export default router;
