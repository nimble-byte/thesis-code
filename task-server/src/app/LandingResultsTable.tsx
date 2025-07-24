import Table from "@/components/Table";
import Link from "next/link";
import { TaskSetSolution } from "@/types/solution";

interface LandingResultsTableProps {
  solutions: TaskSetSolution[];
}

export default function LandingResultsTable({ solutions }: LandingResultsTableProps) {
  const columns = [
    {
      header: "Solution",
      accessor: (row: TaskSetSolution) => <span className="font-mono text-xs">{row.uuid}</span>,
    },
    {
      header: "Set ID",
      accessor: (row: TaskSetSolution) => (
        <span className="font-mono text-xs">{row.setId}</span>
      ),
    },
    {
      header: "Date",
      accessor: (row: TaskSetSolution) => new Date(row.completedAt).toLocaleString(),
    },
    {
      header: "Results",
      accessor: (row: TaskSetSolution) => (
        <Link href={`/solutions/${row.uuid}`} className="text-blue-600 underline hover:text-blue-800">View</Link>
      ),
    },
  ];

  return (
    <div className="w-full max-w-2xl mx-auto mt-8">
      <Table columns={columns} data={solutions} />
    </div>
  );
}
