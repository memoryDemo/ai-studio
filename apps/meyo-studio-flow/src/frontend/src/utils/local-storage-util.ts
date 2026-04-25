import {
  safeGetLocalStorage,
  safeRemoveLocalStorage,
  safeSetLocalStorage,
} from "./browser";

export const getLocalStorage = (key: string) => {
  return safeGetLocalStorage(key);
};

export const setLocalStorage = (key: string, value: string) => {
  safeSetLocalStorage(key, value);
};

export const removeLocalStorage = (key: string) => {
  safeRemoveLocalStorage(key);
};
