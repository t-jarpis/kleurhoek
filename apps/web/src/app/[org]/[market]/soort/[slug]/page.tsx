import { topicPage } from "@/components/TopicPage";

/** Onderwerppagina per soort (ADR 0055). */
const { generateMetadata, Page } = topicPage("soort");
export const revalidate = 300;
export { generateMetadata };
export default Page;
