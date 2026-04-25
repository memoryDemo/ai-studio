import {
  safeGetSessionStorage,
  safeRemoveSessionStorage,
  safeSetSessionStorage,
} from "./browser";

export const getSessionStorage = (key: string) => {
  return safeGetSessionStorage(key);
};

export const setSessionStorage = (key: string, value: string) => {
  safeSetSessionStorage(key, value);
};

export const removeSessionStorage = (key: string) => {
  safeRemoveSessionStorage(key);
};
