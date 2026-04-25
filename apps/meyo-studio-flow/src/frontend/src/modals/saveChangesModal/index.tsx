import { truncate } from "lodash";
import { useCallback, useState } from "react";
import { useTranslation } from "react-i18next";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import Loading from "@/components/ui/loading";
import ConfirmationModal from "../confirmationModal";

export function SaveChangesModal({
  onSave,
  onProceed,
  onCancel,
  flowName,
  lastSaved,
  autoSave,
}: {
  onSave: () => void;
  onProceed: () => void;
  onCancel: () => void;
  flowName: string;
  lastSaved: string | undefined;
  autoSave: boolean;
}): JSX.Element {
  const { t } = useTranslation();
  const [saving, setSaving] = useState(false);
  const flowDisplayName = autoSave
    ? t("saveChanges.flow")
    : truncate(flowName, { length: 32 });

  const handleOpenAutoFocus = useCallback((e: Event) => {
    e.preventDefault();
    (
      document.querySelector('[data-testid="replace-button"]') as HTMLElement
    )?.focus();
  }, []);

  return (
    <ConfirmationModal
      open={true}
      onClose={onCancel}
      destructiveCancel
      title={t("saveChanges.unsavedTitle", { name: flowDisplayName })}
      cancelText={autoSave ? undefined : t("saveChanges.exitAnyway")}
      confirmationText={autoSave ? undefined : t("saveChanges.saveAndExit")}
      onConfirm={
        autoSave
          ? undefined
          : () => {
              setSaving(true);
              onSave();
            }
      }
      onCancel={onProceed}
      loading={autoSave ? true : saving}
      size="x-small"
      onOpenAutoFocus={handleOpenAutoFocus}
    >
      <ConfirmationModal.Content>
        {autoSave ? (
          <div className="mb-4 flex w-full items-center gap-3 rounded-md bg-muted px-4 py-2 text-muted-foreground">
            <Loading className="h-5 w-5" />
            {t("saveChanges.savingChanges")}
          </div>
        ) : (
          <>
            <div className="mb-4 flex w-full items-center gap-3 rounded-md bg-warning px-4 py-2 text-warning-foreground">
              <ForwardedIconComponent name="Info" className="h-5 w-5" />
              {t("saveChanges.lastSaved", {
                value: lastSaved ?? t("saveChanges.never"),
              })}
            </div>
            {t("saveChanges.unsavedLost")}{" "}
            <a
              target="_blank"
              className="text-accent-pink-foreground hover:underline"
              href="https://docs.langflow.org/environment-variables#visual-editor-and-playground-behavior"
              rel="noopener"
            >
              {t("saveChanges.enableAutoSaving")}
            </a>{" "}
            {t("saveChanges.autoSaveSuffix")}
          </>
        )}
      </ConfirmationModal.Content>
    </ConfirmationModal>
  );
}
