import type { ColDef } from "ag-grid-community";
import IconComponent from "@/components/common/genericIconComponent";
import type { TranslationFunction } from "@/types/i18n";
import { formatSmartTimestamp } from "@/utils/dateTime";
import { formatTotalLatency, getStatusIconProps } from "../traceViewHelpers";
import {
  formatObjectValue,
  formatRunValue,
  pickFirstNumber,
} from "./flowTraceColumnsHelpers";

const DEFAULT_TRACE_COLUMN_LABELS: Record<string, string> = {
  "trace.columns.run": "Run",
  "trace.columns.traceId": "Trace ID",
  "trace.columns.timestampUtc": "Timestamp (UTC)",
  "trace.columns.input": "Input",
  "trace.columns.output": "Output",
  "trace.columns.token": "Token",
  "trace.columns.latency": "Latency",
  "trace.columns.status": "Status",
};

export function createFlowTracesColumns({
  flowId,
  flowName,
  t,
}: {
  flowId?: string | null;
  flowName?: string | null;
  t?: TranslationFunction;
} = {}): ColDef[] {
  const translate =
    t ?? ((key: string) => DEFAULT_TRACE_COLUMN_LABELS[key] ?? key);

  return [
    {
      headerName: translate("trace.columns.run"),
      field: "run",
      flex: 1.0,
      minWidth: 240,
      filter: false,
      sortable: false,
      editable: false,
      valueGetter: () => formatRunValue(flowName, flowId),
    },
    {
      headerName: translate("trace.columns.traceId"),
      field: "id",
      flex: 0.3,
      minWidth: 240,
      filter: false,
      sortable: false,
      editable: false,
    },

    {
      headerName: translate("trace.columns.timestampUtc"),
      field: "startTime",
      flex: 0.5,
      minWidth: 70,
      filter: false,
      sortable: false,
      editable: false,
      valueGetter: (params) => formatSmartTimestamp(params.data?.startTime),
    },
    {
      headerName: translate("trace.columns.input"),
      field: "input",
      flex: 1,
      minWidth: 150,
      filter: false,
      sortable: false,
      editable: false,
      valueGetter: (params) => formatObjectValue(params.data?.input),
    },
    {
      headerName: translate("trace.columns.output"),
      field: "output",
      flex: 1,
      minWidth: 150,
      filter: false,
      sortable: false,
      editable: false,
      valueGetter: (params) => formatObjectValue(params.data?.output),
    },
    {
      headerName: translate("trace.columns.token"),
      field: "totalTokens",
      flex: 0.5,
      minWidth: 50,
      filter: false,
      sortable: false,
      editable: false,
      valueGetter: (params) => {
        const tokens = pickFirstNumber(
          params.data?.totalTokens,
          params.data?.total_tokens,
        );
        return tokens === null ? "" : String(tokens);
      },
    },
    {
      headerName: translate("trace.columns.latency"),
      field: "totalLatencyMs",
      flex: 0.6,
      minWidth: 50,
      filter: false,
      sortable: false,
      editable: false,
      valueGetter: (params) => {
        const latencyMs = pickFirstNumber(
          params.data?.totalLatencyMs,
          params.data?.total_latency_ms,
        );
        return formatTotalLatency(latencyMs);
      },
    },
    {
      headerName: translate("trace.columns.status"),
      field: "status",
      flex: 0.6,
      minWidth: 100,
      filter: false,
      sortable: false,
      editable: false,
      cellRenderer: (params: { value: string | null | undefined }) => {
        const status = params.value ?? "unknown";
        const { colorClass, iconName, shouldSpin } = getStatusIconProps(status);

        return (
          <div className="flex items-center">
            <IconComponent
              name={iconName}
              className={`h-4 w-4 ${colorClass} ${shouldSpin ? "animate-spin" : ""}`}
              aria-label={status}
              dataTestId={`flow-log-status-${status}`}
              skipFallback
            />
          </div>
        );
      },
    },
  ];
}
