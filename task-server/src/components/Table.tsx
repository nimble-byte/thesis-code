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
    <table
      style={{
        borderCollapse: "separate",
        borderSpacing: 0,
        width: "100%",
        borderRadius: 8,
      }}
    >
      <thead>
        <tr>
          {columns.map((col, idx) => (
            <th
              key={idx}
              style={{
                padding: "8px 16px",
                textAlign: "left",
                borderBottom: "2px solid #eaeaea",
                fontWeight: 600,
                fontSize: "1.1rem",
                color: "#222",
                backgroundColor: "#00000011",
              }}
            >
              {col.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i} style={{ borderBottom: "2px solid #eaeaea" }}>
            {columns.map((col, j) => (
              <td
                key={j}
                style={{
                  padding: "8px 16px",
                  color: "#333",
                }}
              >
                {col.accessor(row)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
