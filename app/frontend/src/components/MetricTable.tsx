import type { FindingsTable } from "../api";

const fmt = (col: string, v: string | number): string => {
  if (typeof v === "string") return v;
  if (col.includes("($)")) return `${v < 0 ? "−" : ""}$${Math.abs(Math.round(v)).toLocaleString("en-US")}`;
  return Number.isInteger(v) ? String(v) : v.toFixed(4);
};

type Props = { table: FindingsTable; columns: string[]; mutedColumns?: string[] };

export default function MetricTable({ table, columns, mutedColumns = [] }: Props) {
  return (
    <div>
      <p className="muted small">Scope: {table.scope}</p>
      {table.caveat && <p className="caveat">{table.caveat}</p>}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {columns.map((c) => (
                <th key={c} className={typeof table.rows[0]?.[c] === "number" ? "num" : ""}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.rows.map((r, i) => (
              <tr key={i}>
                {columns.map((c) => (
                  <td key={c}
                      className={`${typeof r[c] === "number" ? "num" : ""} ${mutedColumns.includes(c) ? "muted" : ""} ${
                        c.startsWith("Net Benefit") ? (Number(r[c]) < 0 ? "bad" : "good") : ""}`}>
                    {fmt(c, r[c])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
