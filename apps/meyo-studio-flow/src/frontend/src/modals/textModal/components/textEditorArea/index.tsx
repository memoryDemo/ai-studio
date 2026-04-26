import { useTranslation } from "react-i18next";
import { Textarea } from "../../../../components/ui/textarea";

const TextEditorArea = ({
  left,
  value,
  resizable = true,
  onChange,
  readonly,
}: {
  left: boolean | undefined;
  resizable?: boolean;
  value: unknown;
  onChange?: (value: string) => void;
  readonly: boolean;
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

  return (
    <Textarea
      readOnly={readonly}
      className={`w-full custom-scroll ${left ? "min-h-32" : "h-full"} ${
        resizable ? "resize-y" : "resize-none"
      }`}
      placeholder={t("common.empty")}
      // update to real value on flowPool
      value={textValue}
      onChange={(e) => {
        if (onChange) onChange(e.target.value);
      }}
    />
  );
};

export default TextEditorArea;
