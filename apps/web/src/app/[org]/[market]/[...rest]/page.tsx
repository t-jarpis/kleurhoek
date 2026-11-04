import { notFound } from "next/navigation";

/**
 * Elk onbekend adres binnen een markt: de eigen 404 van de markt (not-found.tsx), binnen de layout van de markt,
 * dus met de juiste taal op <html> en een hoofdgebied. Zonder deze route toont Next zijn kale standaardpagina.
 */
export default function UnknownPage() {
  notFound();
}
