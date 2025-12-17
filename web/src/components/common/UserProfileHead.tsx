import { Settings as SettingsIcon } from "@hatchify/icons";
import { useNavigate } from "react-router";

export default function UserProfileHead() {
	const navigate = useNavigate();
	return (
		<div>
			<SettingsIcon
				onClick={() => {
					navigate("/settings");
				}}
				className="size-5 hover:text-primary-1 cursor-pointer"
			/>
		</div>
	);
}
