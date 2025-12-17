import { useState } from "react";

import WebCreatorHeader from "./WebCreatorHeader";
import WebCreatorPreview from "./WebCreatorPreview";

function WebCreator() {
	// const currentTab = useWebCreatorStore((state) => state.currentTab);
	// const reset = useWebCreatorStore((state) => state.reset);
	const [_isMounted, _setIsMountedd] = useState(false);

	// const handleCompile = async () => {
	// 	const result = await buildRT.workerRt.build({ isDev: true });
	// 	setPreviewResult(result);
	// };
	return (
		<div className="h-full flex flex-col rounded-xl overflow-hidden">
			<WebCreatorHeader />
			<div className="flex-1 overflow-hidden">
				<div className="flex flex-1 justify-center h-full ">
					<WebCreatorPreview />
				</div>
			</div>
		</div>
	);
}

export default WebCreator;
