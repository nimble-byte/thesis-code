import React from "react";

export type TableColumn<T> = {
  header: string;
  accessor: (row: T) => React.ReactNode;
};

interface TableProps<T> {
  columns: TableColumn<T>[];
  data: T[];
}

export default function Table<T>({ columns, data }: TableProps<T>) {
  if (!columns) return <div>No columns defined</div>;
  if (!data) data = [];

  return (
    <table style={{ borderCollapse: "collapse", width: "100%" }}>
      <thead>
        <tr>
          {columns.map((col, idx) => (
            <th key={idx} style={{ padding: 8, textAlign: "left" }}>
              {col.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i}>
            {columns.map((col, j) => (
              <td key={j} style={{ padding: 8 }}>
                {col.accessor(row)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
