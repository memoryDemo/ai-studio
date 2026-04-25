import type { AgGridReact } from "ag-grid-react";
import { useCallback, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { Button } from "@/components/ui/button";
import TableModal from "@/modals/tableModal";
import type { ColumnField } from "@/types/utils/functions";
import { FormatterType } from "@/types/utils/functions";
import { FormatColumns } from "@/utils/utils";
import type { ColumnConfigRow } from "../../types";

interface ColumnConfigProps {
  columnConfig: ColumnConfigRow[];
  onColumnConfigChange: (value: ColumnConfigRow[]) => void;
}

export function ColumnConfig({
  columnConfig,
  onColumnConfigChange,
}: ColumnConfigProps) {
  const { t } = useTranslation();
  const columnConfigColumns: ColumnField[] = useMemo(
    () => [
      {
        name: "column_name",
        display_name: t("knowledgeUpload.columnConfig.columnName"),
        sortable: true,
        filterable: true,
        formatter: FormatterType.text,
        description: t("knowledgeUpload.columnConfig.columnNameDescription"),
        edit_mode: "inline",
      },
      {
        name: "vectorize",
        display_name: t("knowledgeUpload.columnConfig.vectorize"),
        sortable: false,
        filterable: false,
        formatter: FormatterType.boolean,
        description: t("knowledgeUpload.columnConfig.vectorizeDescription"),
        default: false,
        edit_mode: "inline",
      },
      {
        name: "identifier",
        display_name: t("knowledgeUpload.columnConfig.identifier"),
        sortable: false,
        filterable: false,
        formatter: FormatterType.boolean,
        description: t("knowledgeUpload.columnConfig.identifierDescription"),
        default: false,
        edit_mode: "inline",
      },
    ],
    [t],
  );
  const AgColumns = FormatColumns(columnConfigColumns);
  const agGrid = useRef<AgGridReact>(null);
  const [isTableModalOpen, setIsTableModalOpen] = useState(false);
  const nextRowId = useRef(0);

  function withRowId(row: ColumnConfigRow) {
    return { ...row, _rowId: String(nextRowId.current++) };
  }

  const [tempColumnConfig, setTempColumnConfig] = useState(() =>
    columnConfig.map((row) => withRowId(row)),
  );

  function getGridRows() {
    const rows: Array<ColumnConfigRow & { _rowId: string }> = [];
    if (agGrid.current && !agGrid.current.api.isDestroyed()) {
      agGrid.current.api.forEachNode((node) => rows.push(node.data));
    }
    return rows;
  }

  function syncFromGrid() {
    setTempColumnConfig(getGridRows());
  }

  const getRowId = useCallback(
    (params: { data: { _rowId: string } }) => params.data._rowId,
    [],
  );

  function addRow() {
    if (agGrid.current && !agGrid.current.api.isDestroyed()) {
      agGrid.current.api.stopEditing();
    }
    setTempColumnConfig([
      ...getGridRows(),
      withRowId({ column_name: "", vectorize: false, identifier: false }),
    ]);
  }

  function deleteRow() {
    if (agGrid.current) {
      agGrid.current.api.stopEditing();
      const selectedNodes = agGrid.current.api.getSelectedNodes();
      if (selectedNodes.length > 0) {
        agGrid.current.api.applyTransaction({
          remove: selectedNodes.map((node) => node.data),
        });
        syncFromGrid();
      }
    }
  }

  function duplicateRow() {
    if (agGrid.current) {
      agGrid.current.api.stopEditing();
      const selectedNodes = agGrid.current.api.getSelectedNodes();
      if (selectedNodes.length > 0) {
        const toDuplicate = selectedNodes.map((node) =>
          withRowId({ ...node.data }),
        );
        setTempColumnConfig([...getGridRows(), ...toDuplicate]);
      }
    }
  }

  function handleTableSave() {
    if (agGrid.current && !agGrid.current.api.isDestroyed()) {
      agGrid.current.api.stopEditing();
      const rows: ColumnConfigRow[] = [];
      agGrid.current.api.forEachNode((node) => {
        const { _rowId, ...rest } = node.data;
        rows.push(rest);
      });
      onColumnConfigChange(rows);
    } else {
      onColumnConfigChange(tempColumnConfig);
    }
    setIsTableModalOpen(false);
  }

  function handleTableCancel() {
    setTempColumnConfig(columnConfig.map((row) => withRowId(row)));
    setIsTableModalOpen(false);
  }

  const editable = columnConfigColumns.map((column) => ({
    field: column.name,
    onUpdate: () => syncFromGrid(),
    editableCell: true,
  }));

  return (
    <TableModal
      open={isTableModalOpen}
      setOpen={(open) => {
        if (open) {
          setTempColumnConfig(columnConfig.map((row) => withRowId(row)));
        }
        setIsTableModalOpen(open);
      }}
      tableTitle={t("knowledgeUpload.columnConfig.title")}
      description={t("knowledgeUpload.columnConfig.description")}
      ref={agGrid}
      onSelectionChanged={() => {}}
      rowSelection="multiple"
      editable={editable}
      pagination={true}
      addRow={addRow}
      onDelete={deleteRow}
      onDuplicate={duplicateRow}
      displayEmptyAlert={false}
      className="h-full w-full"
      columnDefs={AgColumns}
      rowData={tempColumnConfig}
      getRowId={getRowId}
      context={{}}
      stopEditingWhenCellsLoseFocus={true}
      autoSizeStrategy={{
        type: "fitGridWidth",
        defaultMinWidth: 100,
      }}
      onSave={handleTableSave}
      onCancel={handleTableCancel}
    >
      <Button variant="outline" className="w-full justify-center">
        <span className="flex items-center gap-2">
          <ForwardedIconComponent name="Columns" className="h-4 w-4" />
          {t("knowledgeUpload.columnConfig.openTable")}
        </span>
      </Button>
    </TableModal>
  );
}
