import { Workbench } from "@/components/workbench";
import { loadTestQuestions } from "@/lib/testset";

export default async function Page() {
  return <Workbench questions={await loadTestQuestions()} />;
}
