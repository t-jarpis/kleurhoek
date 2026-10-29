import { topicPage } from "@/components/TopicPage";

/** Onderwerppagina per leeftijd (ADR 0055). */
const { generateMetadata, Page } = topicPage("leeftijd");
export const revalidate = 300;
export { generateMetadata };
export default Page;
