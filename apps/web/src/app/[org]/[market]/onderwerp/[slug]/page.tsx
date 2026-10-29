import { topicPage } from "@/components/TopicPage";

/** Onderwerppagina per onderwerp (ADR 0055). */
const { generateMetadata, Page } = topicPage("onderwerp");
export const revalidate = 300;
export { generateMetadata };
export default Page;
