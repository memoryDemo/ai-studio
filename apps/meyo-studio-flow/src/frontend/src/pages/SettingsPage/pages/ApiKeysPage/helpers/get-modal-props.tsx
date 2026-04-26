import type { TranslationFunction } from "@/types/i18n";

export const getModalPropsApiKey = (t: TranslationFunction) => {
  const modalProps = {
    title: t("apiKeys.createTitle"),
    description: t("apiKeys.createDescription"),
    inputPlaceholder: t("apiKeys.inputPlaceholder"),
    buttonText: t("apiKeys.generateButton"),
    generatedKeyMessage: (
      <>
        {" "}
        {t("apiKeys.generatedKeyMessageBefore")}{" "}
        <strong>{t("apiKeys.generatedKeyMessageStrong")}</strong>{" "}
        {t("apiKeys.generatedKeyMessageAfter")}
      </>
    ),
    showIcon: true,
    inputLabel: (
      <>
        <span className="text-sm">{t("flowSettings.description")}</span>{" "}
        <span className="text-xs text-muted-foreground">
          {t("apiKeys.optional")}
        </span>
      </>
    ),
  };

  return modalProps;
};
