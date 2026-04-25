import { useState } from "react";
import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { Button } from "@/components/ui/button";
import { SidebarProvider } from "@/components/ui/sidebar";
import { useCustomNavigate } from "@/customization/hooks/use-custom-navigate";
import { track } from "@/customization/utils/analytics";
import useAddFlow from "@/hooks/flows/use-add-flow";
import type { Category } from "@/types/templates/types";
import { cn } from "@/utils/utils";
import type { newFlowModalPropsType } from "../../types/components";
import BaseModal from "../baseModal";
import GetStartedComponent from "./components/GetStartedComponent";
import { Nav } from "./components/navComponent";
import TemplateContentComponent from "./components/TemplateContentComponent";

export default function TemplatesModal({
  open,
  setOpen,
}: newFlowModalPropsType): JSX.Element {
  const [currentTab, setCurrentTab] = useState("get-started");
  const [loading, setLoading] = useState(false);
  const { t } = useTranslation();
  const addFlow = useAddFlow();
  const navigate = useCustomNavigate();
  const { folderId } = useParams();

  const handleFlowCreating = (isCreating: boolean) => {
    setLoading(isCreating);
  };

  const handleCreateBlankFlow = () => {
    if (loading) return;

    handleFlowCreating(true);
    track("New Flow Created", { template: "Blank Flow" });

    addFlow()
      .then((id) => {
        navigate(`/flow/${id}${folderId ? `/folder/${folderId}` : ""}`);
      })
      .finally(() => {
        handleFlowCreating(false);
      });
  };

  // Define categories and their items
  const categories: Category[] = [
    {
      title: t("templates.nav.templates"),
      items: [
        {
          title: t("templates.nav.getStarted"),
          icon: "SquarePlay",
          id: "get-started",
        },
        {
          title: t("templates.nav.allTemplates"),
          icon: "LayoutPanelTop",
          id: "all-templates",
        },
      ],
    },
    {
      title: t("templates.nav.useCases"),
      items: [
        {
          title: t("templates.nav.assistants"),
          icon: "BotMessageSquare",
          id: "assistants",
        },
        {
          title: t("templates.nav.classification"),
          icon: "Tags",
          id: "classification",
        },
        {
          title: t("templates.nav.coding"),
          icon: "TerminalIcon",
          id: "coding",
        },
        {
          title: t("templates.nav.contentGeneration"),
          icon: "Newspaper",
          id: "content-generation",
        },
        { title: t("templates.nav.qAndA"), icon: "Database", id: "q-a" },
        // { title: "Summarization", icon: "Bot", id: "summarization" },
        // { title: "Web Scraping", icon: "CodeXml", id: "web-scraping" },
      ],
    },
    {
      title: t("templates.nav.methodology"),
      items: [
        {
          title: t("templates.nav.prompting"),
          icon: "MessagesSquare",
          id: "chatbots",
        },
        { title: t("templates.nav.rag"), icon: "Database", id: "rag" },
        { title: t("templates.nav.agents"), icon: "Bot", id: "agents" },
      ],
    },
  ];

  return (
    <BaseModal size="templates" open={open} setOpen={setOpen} className="p-0">
      <BaseModal.Content className="flex flex-col p-0">
        <div className="flex h-full">
          <SidebarProvider width="15rem" defaultOpen={false}>
            <Nav
              categories={categories}
              currentTab={currentTab}
              setCurrentTab={setCurrentTab}
            />
            <main className="flex flex-1 flex-col gap-4 overflow-auto p-6 md:gap-8">
              {currentTab === "get-started" ? (
                <GetStartedComponent
                  loading={loading}
                  onFlowCreating={handleFlowCreating}
                />
              ) : (
                <TemplateContentComponent
                  currentTab={currentTab}
                  categories={categories.flatMap((category) => category.items)}
                  loading={loading}
                  onFlowCreating={handleFlowCreating}
                />
              )}
              <BaseModal.Footer>
                <div className="flex w-full flex-col justify-between gap-4 pb-4 sm:flex-row sm:items-center">
                  <div className="flex flex-col items-start justify-center">
                    <div className="font-semibold">
                      {t("templates.startFromScratch")}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {t("templates.startFromScratchDescription")}
                    </div>
                  </div>
                  <Button
                    onClick={handleCreateBlankFlow}
                    size="sm"
                    data-testid="blank-flow"
                    className={cn(
                      "shrink-0",
                      loading ? "cursor-default opacity-80" : "cursor-pointer",
                    )}
                  >
                    <ForwardedIconComponent
                      name="Plus"
                      className="h-4 w-4 shrink-0"
                    />
                    {t("templates.blankFlow")}
                  </Button>
                </div>
              </BaseModal.Footer>
            </main>
          </SidebarProvider>
        </div>
      </BaseModal.Content>
    </BaseModal>
  );
}
