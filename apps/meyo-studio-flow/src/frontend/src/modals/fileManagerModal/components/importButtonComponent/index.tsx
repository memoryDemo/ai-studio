import { useTranslation } from "react-i18next";
import { MorphingMenu } from "@/components/ui/morphing-menu";

export default function ImportButtonComponent({
  variant = "large",
}: {
  variant?: "large" | "small";
}) {
  const { t } = useTranslation();
  const items = [
    {
      icon: "GoogleDrive",
      label: t("files.importDrive"),
      onClick: () => {
        // Handle Google Drive click
      },
    },
    {
      icon: "OneDrive",
      label: t("files.importOneDrive"),
      onClick: () => {
        // Handle OneDrive click
      },
    },
    {
      icon: "AWSInverted",
      label: t("files.importS3Bucket"),
      onClick: () => {
        // Handle S3 click
      },
    },
  ];

  return (
    <MorphingMenu variant={variant} trigger={t("files.importFrom")} items={items} />
  );
}
