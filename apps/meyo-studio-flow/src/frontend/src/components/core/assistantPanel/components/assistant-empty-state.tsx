import { useTranslation } from "react-i18next";
import meyoAssistantIcon from "@/assets/meyo-icon-square.png";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { Button } from "@/components/ui/button";

interface AssistantEmptyStateProps {
  onSuggestionClick: (suggestion: string) => void;
}

export function AssistantEmptyState({
  onSuggestionClick,
}: AssistantEmptyStateProps) {
  const { t } = useTranslation();
  const suggestions = [
    {
      id: "build-agents",
      icon: "Sparkles",
      text: t("assistant.suggestionBuildAgents"),
    },
    {
      id: "answer-questions",
      icon: "Sparkles",
      text: t("assistant.suggestionAnswerQuestions"),
    },
  ];

  return (
    <div className="flex flex-1 flex-col items-center justify-center px-8">
      <div className="mb-6 flex h-16 w-16 items-center justify-center overflow-hidden rounded-2xl">
        <img
          src={meyoAssistantIcon}
          alt="Meyo Assistant"
          className="h-full w-full object-cover"
        />
      </div>
      <h3 className="mb-6 text-center text-base font-semibold leading-6 tracking-normal text-foreground">
        {t("assistant.welcome")}
      </h3>
      <div className="flex flex-col items-center gap-2">
        {suggestions.map((suggestion) => (
          <Button
            key={suggestion.id}
            variant="outline"
            className="h-[46px] w-[265px] justify-start gap-2 rounded-xl border border-border bg-muted/50 px-3 text-[13px] font-medium leading-4 text-foreground hover:bg-muted"
            onClick={() => onSuggestionClick(suggestion.text)}
          >
            <ForwardedIconComponent
              name={suggestion.icon}
              className="h-5 w-5 text-foreground"
            />
            {suggestion.text}
          </Button>
        ))}
      </div>
    </div>
  );
}
