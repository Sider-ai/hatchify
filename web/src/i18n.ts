import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import { resources } from "@/types/resources";

const LANGUAGE_KEY = "language";

i18n.use(initReactI18next).init({
	lng: localStorage.getItem(LANGUAGE_KEY) || "en",
	fallbackLng: "en",
	resources,
	interpolation: {
		escapeValue: false,
	},
});

i18n.on("languageChanged", (lng) => {
	localStorage.setItem(LANGUAGE_KEY, lng);
});

window.addEventListener("storage", (event) => {
	if (event.key === LANGUAGE_KEY && event.newValue)
		i18n.changeLanguage(event.newValue);
});

export default i18n;
