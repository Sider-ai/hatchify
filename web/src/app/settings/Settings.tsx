import {
	CloseOutlineS as CloseIcon,
	ArrowDown as DropdownIcon,
} from "@hatchify/icons";
import { Dropdown, type MenuProps } from "antd";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";
import type { Theme } from "@/components/provider/ThemeProvider";
import { useTheme } from "@/hooks/useTheme";

function Settings() {
	const { t, i18n } = useTranslation();
	const languageItems: { label: string; key: string }[] = [
		{ label: t("languages.en"), key: "en" },
		{ label: t("languages.zh_CN"), key: "zh_CN" },
	];

	const { theme, setTheme } = useTheme();

	const navigate = useNavigate();

	const items: MenuProps["items"] = [
		{
			label: t("settings.dark"),
			key: "dark",
		},
		{
			label: t("settings.light"),
			key: "light",
		},
		{
			label: t("settings.system"),
			key: "system",
		},
	];

	const handleThemeChange = (key: string) => {
		setTheme(key as Theme);
	};

	const handleLanguageChange = (key: string) => {
		i18n.changeLanguage(key);
	};

	return (
		<div className="w-full h-full p-2">
			<div className="w-full h-full bg-grey-layer1-white rounded-xl">
				<header className="w-full px-5 h-14 flex justify-end items-center">
					<button
						type="button"
						onClick={() => navigate(-1)}
						aria-label={t("common.back")}
					>
						<CloseIcon className="text-text-primary-1 size-5 cursor-pointer" />
					</button>
				</header>
				<div className="mt-8 mx-auto w-[720px]">
					<h4 className="font-dmSans font-semibold text-text-primary-1 text-xl mt-8">
						{t("settings.appearance")}
					</h4>
					<div className="mt-4 px-6 rounded-xl border border-grey-line1-normal shadow-near">
						<div className="h-16 border-b border-grey-line1-normal flex justify-between items-center">
							<span className="text-text-primary-1 font-dmSans text-base font-semibold">
								{t("settings.displayMode")}
							</span>
							<Dropdown
								menu={{
									items,
									onClick: (info) => handleThemeChange(info.key as string),
								}}
								trigger={["click"]}
							>
								<button className="px-4 w-[240px] h-[40px] flex items-center justify-between border border-grey-line2-normal rounded-xl group hover:bg-grey-fill1-hover hover:border-grey-line2-hover">
									<span className="text-text-primary-3 text-base font-dmSans group-hover:text-text-primary-1">
										{t(`settings.${theme}`)}
									</span>
									<DropdownIcon className="text-text-primary-3" />
								</button>
							</Dropdown>
						</div>
						{/* Display Language */}
						<div className="h-16 flex justify-between items-center">
							<span className="text-text-primary-1 font-dmSans text-base font-semibold">
								{t("settings.displayLanguage")}
							</span>
							<Dropdown
								menu={{
									items: languageItems,
									onClick: (info) => handleLanguageChange(info.key as string),
								}}
								trigger={["click"]}
							>
								<button className="px-4 w-[240px] h-[40px] flex items-center justify-between border border-grey-line2-normal rounded-xl group hover:bg-grey-fill1-hover hover:border-grey-line2-hover">
									<span className="text-text-primary-3 text-base font-dmSans group-hover:text-text-primary-1">
										{
											languageItems.find((item) => item.key === i18n.language)
												?.label
										}
									</span>
									<DropdownIcon className="text-text-primary-3" />
								</button>
							</Dropdown>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}

export default Settings;
