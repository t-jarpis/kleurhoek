import { topicPage } from "@/components/TopicPage";

/** Onderwerppagina per werelddeel (ADR 0055). */
const { generateMetadata, Page } = topicPage("werelddeel");
export const revalidate = 300;
export { generateMetadata };
export default Page;
