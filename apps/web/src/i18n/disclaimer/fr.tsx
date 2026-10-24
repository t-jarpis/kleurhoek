import Link from "next/link";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Frans (ADR 0026), vertaling van nl.tsx met dezelfde opbouw. */
export function Disclaimer({ market, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Dernière mise à jour le 24&nbsp;octobre&nbsp;2026.</p>
      <p>Sur cette page, vous découvrirez ce que vous pouvez faire avec les coloriages et les bricolages de Kleurhoek, comment nous renvoyons vers d&apos;autres sites web et comment nous signaler quelque chose. En utilisant Kleurhoek, vous acceptez ces conditions.</p>

      <h2>Tout est dessiné par nous</h2>
      <p>Tous les coloriages, modèles à découper et maquettes de Kleurhoek sont dessinés spécialement pour Kleurhoek. Nous ne copions aucun dessin provenant d&apos;autres sites web ou de livres, et nous ne reproduisons aucun personnage, aucune marque ni aucune figure connue. Les droits d&apos;auteur sur les dessins et sur ce site appartiennent à Kleurhoek.</p>
      <p>Vous pouvez utiliser les coloriages gratuitement&nbsp;:</p>
      <ul>
        <li>à la maison, pour les colorier, les imprimer et les distribuer à la famille et aux amis&nbsp;;</li>
        <li>à l&apos;école, à la crèche, dans une association ou à la bibliothèque, même en grand nombre&nbsp;;</li>
        <li>lors d&apos;une fête, par exemple comme activité de bricolage.</li>
      </ul>
      <p>Ce qui n&apos;est pas permis sans notre accord écrit&nbsp;: vendre les coloriages (à l&apos;unité, dans un cahier ou en téléchargement), les publier sur un autre site web, dans une application ou sur les réseaux sociaux comme s&apos;il s&apos;agissait de votre propre matériel, ou les utiliser dans des produits ou de la publicité. Vous pouvez en revanche les partager avec un lien vers le coloriage sur Kleurhoek.</p>

      <h2>Thèmes chez les créateurs</h2>
      <p>Les enfants cherchent souvent des coloriages de personnages de dessins animés, de parcs d&apos;attractions ou de livres. Ces dessins appartiennent à leurs créateurs, et nous n&apos;avons pas le droit de les dessiner nous-mêmes ni de les copier. Beaucoup de créateurs en proposent toutefois gratuitement sur leur propre site. Dans <Link href={`/${market}/themas`}>Thèmes chez les créateurs</Link>, nous rassemblons des liens vers ces pages. Les règles suivantes s&apos;appliquent&nbsp;:</p>
      <ul>
        <li>Nous renvoyons uniquement vers le site officiel du créateur ou de l&apos;ayant droit, jamais vers des sites qui reprennent les dessins d&apos;autrui.</li>
        <li>Nous n&apos;affichons et ne stockons aucune image, aucun dessin ni aucun logo du créateur. Chez nous, vous ne voyez qu&apos;une description rédigée par nos soins et un lien. Il ne peut en être autrement que si un créateur nous en donne l&apos;autorisation écrite&nbsp;; cela est alors indiqué.</li>
        <li>Chaque lien est vérifié par nous avant sa mise en ligne. Ensuite, un programme informatique contrôle chaque jour si la page existe toujours. Si une page disparaît, nous retirons le lien automatiquement. Nous respectons toujours les règles (robots.txt) du site du créateur.</li>
        <li>Le contenu des sites des créateurs relève de leur propre responsabilité et de leurs propres conditions. Nous n&apos;avons aucune influence sur celui-ci.</li>
      </ul>
      <p>Vous êtes créateur et souhaitez que nous modifiions ou retirions un lien, ou au contraire travailler avec nous&nbsp;? <Link href={contact("partnership")}>Contactez-nous</Link>. Nous effectuons la modification dans un délai de cinq jours ouvrables.</p>

      <h2>Marques et noms</h2>
      <p>Les noms de personnages, de parcs d&apos;attractions, de séries et de marques appartiennent à leurs propriétaires. Nous les utilisons uniquement pour indiquer où trouver quelque chose. Kleurhoek n&apos;est pas lié à ces propriétaires et n&apos;est pas sponsorisé par eux, sauf mention expresse.</p>

      <h2>Liens partenaires</h2>
      <p>Pour certains coloriages et thèmes, nous citons du matériel que vous pouvez utiliser, comme des ciseaux pour enfants ou des crayons de couleur. Il s&apos;agit de liens partenaires&nbsp;: si vous achetez quelque chose via un tel lien, Kleurhoek reçoit une petite commission du magasin. Vous payez le même prix. C&apos;est ainsi que les coloriages restent gratuits. Les liens partenaires sont toujours clairement signalés. Le magasin est responsable du produit, du prix et de la livraison.</p>

      <h2>Signaler une atteinte au droit d&apos;auteur</h2>
      <p>Vous pensez que Kleurhoek contient quelque chose sur lequel vous détenez des droits, ou qu&apos;un lien renvoie vers un contenu qui ne devrait pas s&apos;y trouver&nbsp;? Signalez-le via le <Link href={contact("copyright")}>formulaire de contact</Link> avec l&apos;objet &laquo;&nbsp;Droit d&apos;auteur&nbsp;&raquo;. Indiquez la page concernée, pourquoi elle pose problème selon vous et comment nous pouvons vous joindre. Nous répondons dans un délai de cinq jours ouvrables et, si cela se justifie, nous retirons le contenu le temps de vérifier.</p>

      <h2>Bricoler en toute sécurité</h2>
      <p>Les modèles à découper et les maquettes sont conçus pour être réalisés avec un adulte. Utilisez des ciseaux pour enfants et, pour les lampions, toujours une lumière LED, jamais une vraie bougie. Les petites pièces ne conviennent pas aux enfants de moins de trois ans.</p>

      <h2>Responsabilité</h2>
      <p>Nous réalisons Kleurhoek avec beaucoup de soin, mais nous ne pouvons pas garantir que tout soit toujours exempt d&apos;erreurs ni que le site soit toujours accessible. Dans la mesure permise par la loi, Kleurhoek ne peut être tenu responsable des dommages résultant de l&apos;utilisation du site, des coloriages ou des sites vers lesquels nous renvoyons.</p>

      <h2>Vie privée</h2>
      <p>Nous n&apos;utilisons pas de cookies de suivi ni de régies publicitaires. Nous comptons les visites de façon anonyme&nbsp;: sans cookies, sans adresse IP et sans rien qui permette de remonter jusqu&apos;à vous. Aucun compte n&apos;est nécessaire. Si vous nous envoyez un message, nous utilisons votre nom et votre adresse e-mail uniquement pour vous répondre, et nous conservons le message douze mois au maximum. Vous souhaitez que nous supprimions votre message plus tôt&nbsp;? <Link href={contact("privacy")}>Dites-le-nous</Link>.</p>

      <h2>Modifications et questions</h2>
      <p>Nous pouvons modifier ces conditions, par exemple lorsque quelque chose de nouveau arrive sur Kleurhoek. La date de la dernière mise à jour figure en haut de la page. Ces conditions sont régies par le droit néerlandais. Des questions&nbsp;? <Link href={contact()}>Contactez-nous</Link>.</p>
    </>
  );
}
