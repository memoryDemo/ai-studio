const normalizeBasePath = (value: string | undefined): string => {
  if (!value) {
    return "";
  }

  const trimmed = value.trim();
  if (!trimmed || trimmed === "/") {
    return "";
  }

  const prefixed = trimmed.startsWith("/") ? trimmed : `/${trimmed}`;
  return prefixed.endsWith("/") ? prefixed : `${prefixed}/`;
};

const normalizeApiPath = (
  value: string | undefined,
  fallback: string,
): string => {
  const normalized = normalizeBasePath(value);
  return normalized || fallback;
};

const getBuildEnv = (key: string): string | undefined => {
  if (typeof process !== "undefined" && process.env?.[key]) {
    return process.env[key];
  }

  return import.meta.env?.[key];
};

export const BASENAME = normalizeBasePath(getBuildEnv("VITE_LANGFLOW_BASENAME"));
export const PORT = 3000;
export const PROXY_TARGET = "http://localhost:7860";
export const API_ROUTES = ["^/api/v1/", "^/api/v2/", "/health"];
export const BASE_URL_API = normalizeApiPath(
  getBuildEnv("VITE_LANGFLOW_BASE_URL_API"),
  `${BASENAME || "/"}api/v1/`,
);
export const BASE_URL_API_V2 = normalizeApiPath(
  getBuildEnv("VITE_LANGFLOW_BASE_URL_API_V2"),
  `${BASENAME || "/"}api/v2/`,
);
export const HEALTH_CHECK_URL = "/health_check";
export const DOCS_LINK = "https://docs.langflow.org";

export default {
  DOCS_LINK,
  BASENAME,
  PORT,
  PROXY_TARGET,
  API_ROUTES,
  BASE_URL_API,
  BASE_URL_API_V2,
  HEALTH_CHECK_URL,
};
