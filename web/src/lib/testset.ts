import "server-only";
import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Category, TestQuestion } from "@/lib/types";

// The same 41 questions the eval harness runs (eval/testset-v2.csv at the repo root).
const TESTSET = path.join(process.cwd(), "..", "eval", "testset-v2.csv");

/** Minimal RFC 4180 parser: quoted fields, doubled quotes, commas and newlines inside quotes. */
function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') {
        field += '"';
        i++;
      } else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ",") {
      row.push(field);
      field = "";
    } else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field);
      if (row.some(Boolean)) rows.push(row);
      row = [];
      field = "";
    } else field += c;
  }
  row.push(field);
  if (row.some(Boolean)) rows.push(row);
  return rows;
}

export async function loadTestQuestions(): Promise<TestQuestion[]> {
  "use cache";
  const [header, ...rows] = parseCsv(await readFile(TESTSET, "utf8"));
  const col = (name: string) => header.indexOf(name);
  return rows.map((r) => ({
    id: r[col("id")],
    category: r[col("category")] as Category,
    question: r[col("question")],
    expected: r[col("expected_behavior")],
  }));
}
