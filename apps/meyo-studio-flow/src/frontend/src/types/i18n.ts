import type { UseTranslationResponse } from "react-i18next";

export type TranslationFunction = UseTranslationResponse<
  "translation",
  undefined
>["t"];
