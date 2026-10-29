import { topicPage } from "@/components/TopicPage";

/** Onderwerppagina per feestdag (ADR 0055). */
const { generateMetadata, Page } = topicPage("feestdag");
export const revalidate = 300;
export { generateMetadata };
export default Page;
