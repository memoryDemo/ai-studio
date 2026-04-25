import { useState } from "react";
import { useTranslation } from "react-i18next";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { useSidebar } from "@/components/ui/sidebar";
import { usePostCreateSnapshot } from "@/controllers/API/queries/flow-version";
import useAlertStore from "@/stores/alertStore";
import CanvasBanner, { CanvasBannerButton } from "./CanvasBanner";

interface SaveSnapshotButtonProps {
  flowId: string;
}

export default function SaveSnapshotButton({
  flowId,
}: SaveSnapshotButtonProps) {
  const { t } = useTranslation();
  const setSuccessData = useAlertStore((state) => state.setSuccessData);
  const setErrorData = useAlertStore((state) => state.setErrorData);
  const { setActiveSection, open, toggleSidebar } = useSidebar();
  const { mutate: createSnapshot, isPending: isCreating } =
    usePostCreateSnapshot();
  const [isSavingDisplay, setIsSavingDisplay] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleDismiss = () => {
    // Switching the section unmounts the version sidebar, whose cleanup
    // handles clearPreview, restoring auto-save, and restoring the
    // inspection panel.
    setActiveSection("components");
    if (!open) toggleSidebar();
  };

  const handleSave = () => {
    setIsSavingDisplay(true);
    createSnapshot(
      { flowId, description: null },
      {
        onSuccess: () => {
          setSuccessData({ title: t("flowVersion.versionSaved") });
          setIsSavingDisplay(false);
          setSavedSuccess(true);
        },
        onError: (err: unknown) => {
          const detail =
            err && typeof err === "object" && "response" in err
              ? (err as { response?: { data?: { detail?: string } } }).response
                  ?.data?.detail
              : undefined;
          setErrorData({
            title: t("flowVersion.saveFailed"),
            ...(detail ? { list: [detail] } : {}),
          });
          setIsSavingDisplay(false);
        },
      },
    );
  };

  return (
    <CanvasBanner
      icon="BookMarked"
      title={t("flowVersion.saveTitle")}
      description={t("flowVersion.saveDescription")}
      actionSlot={
        <div className="flex items-center gap-2">
          <CanvasBannerButton variant="outline" onClick={handleDismiss}>
            {t("flowVersion.keepBuilding")}
          </CanvasBannerButton>
          <CanvasBannerButton
            onClick={handleSave}
            disabled={isSavingDisplay || isCreating || savedSuccess}
          >
            {isSavingDisplay || isCreating ? (
              <>
                <ForwardedIconComponent
                  name="Loader2"
                  className="h-3.5 w-3.5 animate-spin"
                />
                {t("flowVersion.saving")}
              </>
            ) : savedSuccess ? (
              <>
                <ForwardedIconComponent name="Check" className="h-3.5 w-3.5" />
                {t("flowVersion.saved")}
              </>
            ) : (
              t("flowVersion.save")
            )}
          </CanvasBannerButton>
        </div>
      }
    />
  );
}
