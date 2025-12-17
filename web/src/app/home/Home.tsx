import { useMutation } from "@tanstack/react-query";
import { useCallback, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";
import { WorkflowApi } from "@/api";
import { workflowTaskId } from "@/utils/taskId";
import Header from "./components/Header";
import InputArea from "./components/InputArea";
import LibrarySection from "./components/LibrarySection";
import PromptSuggestionsSection from "./components/PromptSuggestionsSection";

function HomePage() {
	const { t } = useTranslation();
	const navigate = useNavigate();
	const [inputValue, setInputValue] = useState("");

	const createWorkflowMutation = useMutation({
		mutationFn: async (value: {
			prompt: string;
			isPromptOptimization: boolean;
		}) => {
			if (!value.prompt.trim()) {
				throw new Error(t("home.input.errorPromptRequired"));
			}
			const workflowResponse = await WorkflowApi.createOrUpdateWorkflowStream({
				text: value.prompt,
			});
			return {
				sessionId: workflowResponse.data.session_id,
				executionId: workflowResponse.data.execution_id,
				graphId: workflowResponse.data.graph_id,
			};
		},
		onSuccess: ({ sessionId, executionId, graphId }) => {
			console.log("workflow create success", graphId, sessionId, executionId);
			if (graphId && executionId) {
				workflowTaskId.set(graphId, executionId);
				// No need to invalidate queries since WorkflowList manages its own data
				navigate(`/studio/${graphId}`);
			}
		},
		onError: (error: Error) => {
			console.error("Failed to create workflow:", error);
		},
	});

	const handleSend = useCallback(
		async (value: { prompt: string; isPromptOptimization: boolean }) => {
			await createWorkflowMutation.mutateAsync(value);
		},
		[createWorkflowMutation.mutateAsync],
	);

	return (
		<div className="flex flex-col min-h-screen p-2 bg-grey-layer1-white">
			<div className="flex flex-col  pb-6 px-3 gap-6">
				{/* Header */}
				<Header />

				{/* Hero */}
				<section className="pt-30">
					<div className="flex justify-center items-center gap-4 flex-wrap text-text-primary-1">
						<h1 className="font-[500] font-poppins text-[28px] leading-[32px] text-text-primary-1">
							{t("home.hero.question")}
						</h1>
					</div>
				</section>

				{/* <div className="">
          <ToolsSection />
        </div> */}
				{/* Input */}
				<section className="relative mx-auto max-w-[720px] w-full pb-8 ">
					<InputArea
						onSend={handleSend}
						isLoading={createWorkflowMutation.isPending}
						value={inputValue}
						setValue={setInputValue}
					/>
					<div className="w-full flex items-center justify-center mt-2">
						<PromptSuggestionsSection
							onClick={(prompt) => setInputValue(prompt)}
						/>
					</div>
				</section>

				{/* Library- History Community Tools */}
				<section className="mt-[70px] px-[56px]">
					<LibrarySection />
				</section>
			</div>
		</div>
	);
}

export default HomePage;
