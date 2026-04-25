import { useTranslation } from "react-i18next";
import { cn } from "@/utils/utils";
import { useDeploymentStepper } from "../contexts/deployment-stepper-context";

const CREATE_STEPS = [
  { number: 1, labelKey: "deployments.steps.provider" },
  { number: 2, labelKey: "deployments.steps.type" },
  { number: 3, labelKey: "deployments.steps.attachFlows" },
  { number: 4, labelKey: "deployments.steps.review" },
] as const;

const EDIT_STEPS = [
  { number: 1, labelKey: "deployments.steps.type" },
  { number: 2, labelKey: "deployments.steps.attachFlows" },
  { number: 3, labelKey: "deployments.steps.review" },
] as const;

export const DEPLOYMENT_STEPS = CREATE_STEPS;

export default function DeploymentStepper() {
  const { t } = useTranslation();
  const { currentStep, isEditMode } = useDeploymentStepper();
  const steps = isEditMode ? EDIT_STEPS : CREATE_STEPS;
  const progressPercent = ((currentStep - 1) / (steps.length - 1)) * 100;

  return (
    <div className="relative mx-auto h-[52px] w-full max-w-[700px]">
      <div className="absolute left-4 right-4 top-4 h-[2px] bg-muted">
        <div
          className="h-full bg-foreground transition-all duration-300"
          style={{ width: `${progressPercent}%` }}
        />
      </div>
      <div className="relative flex h-full items-start justify-between">
        {steps.map((step) => (
          <div key={step.number} className="flex flex-col items-center gap-1">
            <div
              className={cn(
                "flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium transition-colors",
                currentStep >= step.number
                  ? "bg-foreground text-background"
                  : "bg-muted text-muted-foreground",
              )}
            >
              {step.number}
            </div>
            <span
              className={cn(
                "whitespace-nowrap text-xs text-foreground",
                currentStep >= step.number && "font-medium",
              )}
            >
              {t(step.labelKey)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
