import { useTranslation } from "react-i18next";
import { Textarea } from "../../../components/ui/textarea";

const TextOutputView = ({
  left,
  value,
}: {
  left: boolean | undefined;
  value: unknown;
}) => {
  const { t } = useTranslation();

  let resolvedValue = value;
  if (
    typeof resolvedValue === "object" &&
    resolvedValue !== null &&
    "text" in resolvedValue
  ) {
    resolvedValue = (resolvedValue as { text?: unknown }).text;
  }

  const textValue =
    typeof resolvedValue === "string"
      ? resolvedValue
      : resolvedValue == null
        ? ""
        : String(resolvedValue);
  const isTruncated = textValue.length > 20000;

  return (
    <>
      {" "}
      <Textarea
        className={`w-full resize-none custom-scroll ${left ? "min-h-32" : "h-full"}`}
        placeholder={t("common.empty")}
        readOnly
        value={textValue}
      />
      {isTruncated && (
        <div className="mt-2 text-xs text-muted-foreground">
          {t("output.truncated")}
        </div>
      )}
    </>
  );
};

export default TextOutputView;
