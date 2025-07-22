import React from "react";
import Table, { TableColumn } from "@/components/Table";
import type { TaskAnswer } from "@/types/solution";

interface TaskReportTableProps {
  answers: TaskAnswer[];
}

const columns: TableColumn<TaskAnswer>[] = [
  {
    header: "ID",
    accessor: (row) => row.pid,
  },
  {
    header: "Question",
    accessor: (row) => row.question || "-",
  },
  {
    header: "Given Answer",
    accessor: (row) => row.givenAnswer,
  },
  {
    header: "Correct Answer",
    accessor: (row) => row.correctAnswer,
  },
  {
    header: "Time Taken",
    accessor: (_row) => "",
  },
];

export default function TaskReportTable({ answers }: TaskReportTableProps) {
  return <Table columns={columns} data={answers} />;
}
