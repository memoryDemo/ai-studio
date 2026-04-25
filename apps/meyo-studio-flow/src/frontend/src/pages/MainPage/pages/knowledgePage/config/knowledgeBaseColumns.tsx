import type { ColDef } from "ag-grid-community";
import type { TFunction } from "i18next";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import LoadingTextComponent from "@/components/common/loadingTextComponent";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { KnowledgeBaseInfo } from "@/controllers/API/queries/knowledge-bases/use-get-knowledge-bases";
import { formatFileSize } from "@/utils/stringManipulation";
import { FILE_ICONS } from "@/utils/styleUtils";
import { cn } from "@/utils/utils";
import {
  formatAverageChunkSize,
  formatNumber,
} from "../utils/knowledgeBaseUtils";
import { isBusyStatus, STATUS_CONFIG } from "./statusConfig";

export interface KnowledgeBaseColumnsCallbacks {
  onViewChunks?: (knowledgeBase: KnowledgeBaseInfo) => void;
  onDelete?: (knowledgeBase: KnowledgeBaseInfo) => void;
  onAddSources?: (knowledgeBase: KnowledgeBaseInfo) => void;
  onStopIngestion?: (knowledgeBase: KnowledgeBaseInfo) => void;
}

const DEFAULT_LABELS: Record<string, string> = {
  "knowledge.columns.name": "Name",
  "knowledge.columns.size": "Size",
  "knowledge.columns.embeddingModel": "Embedding Model",
  "knowledge.columns.chunks": "Chunks",
  "knowledge.columns.avgChunkSize": "Avg Chunk Size",
  "knowledge.columns.status": "Status",
  "knowledge.unknown": "Unknown",
  "knowledge.status.ready": "Ready",
  "knowledge.status.ingesting": "Ingesting",
  "knowledge.status.failed": "Failed",
  "knowledge.status.cancelling": "Cancelling",
  "knowledge.status.empty": "Empty",
  "knowledge.actions.updateKnowledge": "Update Knowledge",
  "knowledge.actions.viewChunks": "View Chunks",
  "knowledge.actions.stopIngestion": "Stop Ingestion",
  "knowledge.actions.delete": "Delete",
};

const fallbackTranslate = (
  key: string,
  options?: { defaultValue?: string },
): string => DEFAULT_LABELS[key] ?? options?.defaultValue ?? key;

export const createKnowledgeBaseColumns = (
  callbacks?: KnowledgeBaseColumnsCallbacks,
  t?: TFunction,
): ColDef[] => {
  const translate: TFunction = t ?? (fallbackTranslate as TFunction);
  const baseCellClass =
    "text-muted-foreground cursor-pointer select-text group-[.no-select-cells]:cursor-default group-[.no-select-cells]:select-none";

  const secondaryCellClass = `text-primary group-[.no-select-cells]:cursor-pointer group-[.no-select-cells]:select-none`;

  return [
    {
      headerName: translate("knowledge.columns.name"),
      field: "name",
      flex: 2,
      sortable: true,
      headerCheckboxSelection: true,
      checkboxSelection: true,
      editable: false,
      cellClass: secondaryCellClass,
      cellStyle: { textTransform: "none" },
      cellRenderer: (params: { data: KnowledgeBaseInfo; value: string }) => {
        const sourceTypes = params.data.source_types ?? [];
        const status = params.data.status ?? "empty";

        let iconName = "File";
        let iconColor: string | undefined = "text-muted-foreground";

        if (status === "empty" || sourceTypes.length === 0) {
          iconName = "File";
          iconColor = "text-muted-foreground";
        } else if (sourceTypes.length === 1) {
          const type = sourceTypes[0] as keyof typeof FILE_ICONS;
          iconName = FILE_ICONS[type]?.icon ?? "File";
          iconColor = FILE_ICONS[type]?.color ?? "text-accent-blue-foreground";
        } else {
          iconName = "Layers";
          iconColor = undefined;
        }

        return (
          <div className="flex items-center gap-4">
            <div className="file-icon pointer-events-none relative">
              <ForwardedIconComponent
                name={iconName}
                className={cn("-mx-[3px] h-6 w-6 shrink-0", iconColor)}
              />
            </div>
            <span>{params.value}</span>
          </div>
        );
      },
    },
    {
      headerName: translate("knowledge.columns.size"),
      field: "size",
      flex: 1,
      sortable: false,
      valueFormatter: (params) => formatFileSize(params.value),
      editable: false,
      cellClass: baseCellClass,
    },
    {
      headerName: translate("knowledge.columns.embeddingModel"),
      field: "embedding_model",
      flex: 1.5,
      sortable: false,
      editable: false,
      cellClass: baseCellClass,
      cellRenderer: (params: { data: KnowledgeBaseInfo }) => {
        const model = params.data.embedding_model || translate("knowledge.unknown");
        const provider =
          params.data.embedding_provider || translate("knowledge.unknown");

        const providerIconMap: Record<string, string> = {
          OpenAI: "OpenAI",
          Anthropic: "Anthropic",
          "Google Generative AI": "GoogleGenerativeAI",
          "IBM WatsonX": "WatsonxAI",
          Ollama: "Ollama",
          NVIDIA: "NVIDIA",
        };

        const iconName = providerIconMap[provider] || "Cpu";

        return (
          <div className="flex items-center gap-2">
            <ForwardedIconComponent
              name={iconName}
              className="h-4 w-4 shrink-0"
            />
            <span className="truncate">{model}</span>
          </div>
        );
      },
    },
    {
      headerName: translate("knowledge.columns.chunks"),
      field: "chunks",
      flex: 1,
      sortable: false,
      editable: false,
      cellClass: baseCellClass,
      valueFormatter: (params) => formatNumber(params.value),
    },
    {
      headerName: translate("knowledge.columns.avgChunkSize"),
      field: "avg_chunk_size",
      flex: 1,
      sortable: false,
      editable: false,
      cellClass: baseCellClass,
      valueFormatter: (params) => formatAverageChunkSize(params.value),
    },
    {
      headerName: translate("knowledge.columns.status"),
      field: "status",
      flex: 1,
      sortable: false,
      editable: false,
      resizable: false,
      cellClass: baseCellClass,
      cellRenderer: (params: { data: KnowledgeBaseInfo }) => {
        const status = params.data?.status || "empty";
        const c = STATUS_CONFIG[status] || STATUS_CONFIG.empty;
        const statusLabel = translate(`knowledge.status.${status}`, {
          defaultValue: c.label,
        });

        return (
          <div className="flex items-center h-full">
            <span className={cn("text-xs font-medium", c.textClass)}>
              {isBusyStatus(status) ? (
                <LoadingTextComponent text={statusLabel} />
              ) : (
                statusLabel
              )}
            </span>
          </div>
        );
      },
    },
    {
      headerName: "",
      field: "actions",
      width: 65,
      minWidth: 65,
      sortable: false,
      editable: false,
      resizable: false,
      suppressMovable: true,
      cellClass: "flex items-center justify-center text-primary",
      cellRenderer: (params: { data: KnowledgeBaseInfo }) => {
        const status = params.data?.status;
        const isBusy = isBusyStatus(status);
        const isCancelling = status === "cancelling";
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={(e) => e.stopPropagation()}
              >
                <ForwardedIconComponent
                  name="EllipsisVertical"
                  className="h-4 w-4 text-primary"
                />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                disabled={isBusy}
                onClick={(e) => {
                  e.stopPropagation();
                  callbacks?.onAddSources?.(params.data);
                }}
              >
                <ForwardedIconComponent
                  name="RefreshCw"
                  className="mr-2 h-4 w-4"
                />
                {translate("knowledge.actions.updateKnowledge")}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  callbacks?.onViewChunks?.(params.data);
                }}
              >
                <ForwardedIconComponent
                  name="Layers"
                  className="mr-2 h-4 w-4"
                />
                {translate("knowledge.actions.viewChunks")}
              </DropdownMenuItem>
              {isBusy ? (
                <DropdownMenuItem
                  disabled={isCancelling}
                  onClick={(e) => {
                    e.stopPropagation();
                    callbacks?.onStopIngestion?.(params.data);
                  }}
                  className="text-destructive focus:text-destructive"
                >
                  <ForwardedIconComponent
                    name="Square"
                    className="mr-2 h-4 w-4"
                  />
                  {translate("knowledge.actions.stopIngestion")}
                </DropdownMenuItem>
              ) : (
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation();
                    callbacks?.onDelete?.(params.data);
                  }}
                  className="text-destructive focus:text-destructive"
                >
                  <ForwardedIconComponent
                    name="Trash2"
                    className="mr-2 h-4 w-4"
                  />
                  {translate("knowledge.actions.delete")}
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];
};
