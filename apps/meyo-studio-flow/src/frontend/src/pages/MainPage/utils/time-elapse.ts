import type { TranslationFunction } from "@/types/i18n";

export const timeElapsed = (
  dateTimeString: string | undefined,
  t?: TranslationFunction,
): string => {
  if (!dateTimeString) {
    return "";
  }

  const givenDate = new Date(dateTimeString);
  const now = new Date();

  const diffInMs = Math.abs(now.getTime() - givenDate.getTime());

  const minutes = Math.floor(diffInMs / (1000 * 60));
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const months = Math.floor(days / 30); // Approximate
  const years = Math.floor(months / 12);

  if (years > 0) {
    return t
      ? t("time.year", { count: years })
      : years === 1
        ? `${years} year`
        : `${years} years`;
  } else if (months > 0) {
    return t
      ? t("time.month", { count: months })
      : months === 1
        ? `${months} month`
        : `${months} months`;
  } else if (days > 0) {
    return t
      ? t("time.day", { count: days })
      : days === 1
        ? `${days} day`
        : `${days} days`;
  } else if (hours > 0) {
    return t
      ? t("time.hour", { count: hours })
      : hours === 1
        ? `${hours} hour`
        : `${hours} hours`;
  } else if (minutes > 0) {
    return t
      ? t("time.minute", { count: minutes })
      : minutes === 1
        ? `${minutes} minute`
        : `${minutes} minutes`;
  } else {
    return t ? t("time.lessThanMinute") : "less than a minute";
  }
};
