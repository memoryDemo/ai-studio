import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import {
  DialogDescription,
  DialogFooter,
  DialogTitle,
} from "@/components/ui/dialog";
import StepDeployStatus from "@/pages/MainPage/pages/deploymentsPage/components/step-deploy-status";

interface UpdatePhaseContentProps {
  isUpdating: boolean;
  isUpdated: boolean;
  deploymentName: string;
  onClose: () => void;
  onTest?: () => void;
}

export default function UpdatePhaseContent({
  isUpdating,
  isUpdated,
  deploymentName,
  onClose,
  onTest,
}: UpdatePhaseContentProps) {
  const { t } = useTranslation();

  return (
    <>
      <DialogTitle className="sr-only">
        {isUpdating
          ? t("deployments.choice.updatingDeployment")
          : t("deployments.choice.deploymentUpdated")}
      </DialogTitle>
      <DialogDescription className="sr-only">
        {isUpdating
          ? t("deployments.choice.updatingDescription")
          : t("deployments.choice.updatedDescription", {
              name: deploymentName,
            })}
      </DialogDescription>
      <StepDeployStatus
        phase={isUpdating ? "deploying" : "deployed"}
        deploymentName={deploymentName}
        loadingTitle={t("deployments.updating")}
        loadingDescription={t("deployments.choice.updatingLongDescription")}
        doneTitle={t("deployments.choice.deploymentUpdated")}
        doneDescription={t("deployments.choice.updatedSuccessDescription", {
          name: deploymentName,
        })}
      />
      {isUpdated && (
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            {t("deployments.close")}
          </Button>
          {onTest && <Button onClick={onTest}>{t("deployments.columns.test")}</Button>}
        </DialogFooter>
      )}
    </>
  );
}
