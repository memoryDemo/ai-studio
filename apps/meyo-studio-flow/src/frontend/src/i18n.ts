import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./locales/en.json";

const languageLoaders = {
  de: () => import("./locales/de.json"),
  en: () => Promise.resolve({ default: en }),
  es: () => import("./locales/es.json"),
  fr: () => import("./locales/fr.json"),
  ja: () => import("./locales/ja.json"),
  pt: () => import("./locales/pt.json"),
  "zh-Hans": () => import("./locales/zh-Hans.json"),
};

type SupportedLanguage = keyof typeof languageLoaders;

const lowerCaseLanguageMap = Object.keys(languageLoaders).reduce(
  (acc, language) => {
    acc[language.toLowerCase()] = language as SupportedLanguage;
    return acc;
  },
  {} as Record<string, SupportedLanguage>,
);

export function normalizeLanguage(lang: string): SupportedLanguage {
  const normalized = lang.trim();
  const lowerCaseLang = normalized.toLowerCase();

  if (lowerCaseLanguageMap[lowerCaseLang]) {
    return lowerCaseLanguageMap[lowerCaseLang];
  }

  if (lowerCaseLang.startsWith("zh")) {
    return "zh-Hans";
  }

  const baseLang = lowerCaseLang.split("-")[0];
  return lowerCaseLanguageMap[baseLang] ?? "en";
}

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
  },
  lng: "en",
  fallbackLng: "en",
  interpolation: {
    escapeValue: false,
  },
});

export async function loadLanguage(lang: string): Promise<void> {
  const language = normalizeLanguage(lang);
  if (language === "en") return;
  if (i18n.hasResourceBundle(language, "translation")) return;
  const messages = await languageLoaders[language]();
  i18n.addResourceBundle(language, "translation", messages.default);
}

export default i18n;
