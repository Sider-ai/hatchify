import { useTranslation } from "react-i18next";

const HeroSection: React.FC = () => {
	const { t } = useTranslation();

	return (
		<section className="pt-30">
			<div className="flex justify-center items-center gap-4 flex-wrap text-text-primary-1">
				{/* <MultiAgentIcon size={40} className="translate-y-1" /> */}
				<h1 className="font-[500] font-poppins text-[28px] leading-[32px] text-text-primary-1">
					{t("home.hero.question")}
				</h1>
				{/* <span className="text-sm text-text-primary-3 font-semibold py-1.5 px-3 rounded-lg border border-grey-line2-normal">
					{t("home.hero.badge")}
				</span> */}
			</div>
			{/* <p className="text-text-primary-3 leading-6 text-center mt-2">
				{t("home.hero.subtitle")}
			</p> */}
		</section>
	);
};
export default HeroSection;
