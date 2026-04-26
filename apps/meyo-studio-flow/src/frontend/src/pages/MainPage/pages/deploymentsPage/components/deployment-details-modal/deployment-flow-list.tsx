import type { DeploymentFlowVersionItem } from "@/controllers/API/queries/deployments/use-get-deployment-attachments";
import { useTranslation } from "react-i18next";
import FlowVersionItem from "./flow-version-item";

interface DeploymentFlowListProps {
  flowVersions: DeploymentFlowVersionItem[];
  getConnectionNames: (fv: DeploymentFlowVersionItem) => string[];
}

export default function DeploymentFlowList({
  flowVersions,
  getConnectionNames,
}: DeploymentFlowListProps) {
  const { t } = useTranslation();

  return (
    <div className="flex flex-col gap-3">
      <span className="text-sm font-medium text-foreground">
        {t("deployments.details.attachedFlows", {
          count: flowVersions.length,
        })}
      </span>
      {flowVersions.length === 0 ? (
        <span className="text-sm text-muted-foreground">
          {t("deployments.details.noFlowsAttached")}
        </span>
      ) : (
        <div className="flex flex-col gap-2">
          {flowVersions.map((fv) => (
            <FlowVersionItem
              key={fv.id}
              flowName={fv.flow_name}
              versionNumber={fv.version_number}
              toolName={fv.provider_data?.tool_name ?? null}
              connectionNames={getConnectionNames(fv)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
