import "./i18n";
import { loadLanguage } from "./i18n";
import ReactDOM from "react-dom/client";
import reportWebVitals from "./reportWebVitals";

import "./style/classes.css";
// @ts-ignore
import "./style/index.css";
// @ts-ignore
import "./App.css";
import "./style/applies.css";

// @ts-ignore
import App from "./customization/custom-App";
import { safeGetLocalStorage, safeNavigatorLanguage } from "./utils/browser";

const detectedLang =
  safeGetLocalStorage("languagePreference") || safeNavigatorLanguage() || "en";

loadLanguage(detectedLang).then(() => {
  const root = ReactDOM.createRoot(
    document.getElementById("root") as HTMLElement,
  );
  (
    window as typeof window & {
      __LF_APP_MOUNTED?: boolean;
    }
  ).__LF_APP_MOUNTED = true;
  root.render(<App />);
  reportWebVitals();
});
