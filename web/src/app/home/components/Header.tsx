import { TextLogo } from "@hatchify/icons";
import UserProfileHead from "@/components/common/UserProfileHead";

function Header() {
	return (
		<header className="flex h-14 w-full px-5 items-center justify-between text-text-primary-1 font-bold text-[24px] ">
			<span>
				<TextLogo className="size-24" />
			</span>
			<div className="flex items-center gap-3">
				<UserProfileHead />
			</div>
		</header>
	);
}

export default Header;
