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
    accessor: (row) => {
      if (!row.startedAt || !row.completedAt) return "";

      const startedAt = new Date(row.startedAt);
      const completedAt = new Date(row.completedAt);
      const timeTaken = completedAt.getTime() - startedAt.getTime();
      const timeTakenSecs = Math.floor(timeTaken / 1000);

      if (timeTakenSecs < 60) return `${timeTakenSecs}s`;

      return `${Math.floor(timeTakenSecs / 60)}m ${timeTakenSecs % 60}s`;
    },
  },
];

export default function TaskReportTable({ answers }: TaskReportTableProps) {
  return <Table columns={columns} data={answers} />;
}
