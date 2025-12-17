import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { supportLangs } from "@/types/resources";

export function useLanguage() {
	const { i18n, t } = useTranslation();

	const changeLanguage = useCallback(
		(language: string) => {
			// if (supportLangs.includes(language))
			i18n.changeLanguage(language);
			// else throw new Error(`Unsupported language: ${language}`)
		},
		[i18n],
	);

	return {
		currentLanguage: i18n.language,
		supportedLanguages: supportLangs,
		changeLanguage,
		t,
	};
}
