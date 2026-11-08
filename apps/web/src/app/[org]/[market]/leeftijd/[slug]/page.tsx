import { topicPage } from "@/components/TopicPage";

/** Onderwerppagina per leeftijd (ADR 0055). */
const { generateMetadata, Page } = topicPage("leeftijd");
export const revalidate = 300;
/** Leeg: de pagina wordt bij het eerste verzoek gemaakt en daarna bewaard (ISR, ADR 0093). */
export function generateStaticParams() { return []; }
export { generateMetadata };
export default Page;
