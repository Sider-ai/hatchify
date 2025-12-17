import { Select } from "antd";
import { ModelApi } from "@/api";

export default function ModelSelecter({
	value,
	onChange,
}: {
	value: string;
	onChange: (value: string) => void;
}) {
	const { modelList } = ModelApi.useModelList();

	const modelOptions = modelList.map((model) => ({
		label: model.id,
		value: model.id,
	}));

	return (
		<Select
			className="w-full"
			value={value}
			onChange={onChange}
			options={modelOptions}
			size="middle"
			popupMatchSelectWidth
		/>
	);
}
