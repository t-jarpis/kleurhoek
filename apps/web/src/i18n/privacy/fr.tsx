import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Dernière mise à jour le 4 novembre 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be et www.kleurhoek.com) est un site de coloriages et de bricolages originaux pour les enfants. Nous collectons le moins de données possible. Cette page indique précisément ce que nous conservons, pourquoi, pendant combien de temps et quels sont vos droits.</p>

      <h2>Qui nous sommes</h2>
      <p>Kleurhoek est un site néerlandais. Pour toute question sur la protection de la vie privée, utilisez notre <Link href={contact("privacy")}>formulaire de contact</Link>.</p>

      <h2>Visiter et colorier</h2>
      <p>Nous comptons les visites de manière anonyme : sans cookies, sans adresses IP et sans rien qui permette de remonter jusqu’à vous. Nous n’utilisons aucun script publicitaire ou de suivi de tiers, y compris de Google, Meta ou Pinterest. Vous pouvez colorier, imprimer et colorier à plusieurs sans compte. Ce que vous coloriez reste sur votre propre appareil. Quand vous coloriez à plusieurs, les traits passent par notre serveur pour rejoindre les autres personnes du salon, sans aucun nom ; après 30 minutes sans coloriage, le salon se ferme. Les noms que vous saisissez pour les étiquettes cadeaux ne sont jamais envoyés à notre serveur.</p>
      <p>Pour ne pas compter deux fois les mêmes visiteurs, nous créons chaque jour un code à partir de votre adresse IP et de votre navigateur, avec une clé qui change tous les jours ; nous ne conservons pas l’adresse IP elle-même. Après 90 jours, nous remplaçons ce code par un code aléatoire, de sorte que même nous ne pouvons plus relier un comptage à un appareil. Nous conservons les comptages eux-mêmes (quelle page, quel pays, téléphone ou ordinateur, quand) afin de voir comment le site est utilisé au fil des années.</p>

      <h2>Compte</h2>
      <p>Les comptes sont réservés aux adultes (16 ans ou plus). Les enfants n’ont pas besoin de compte et ne peuvent pas en créer. Si vous avez un compte, nous conservons votre nom, votre adresse e-mail et vos favoris, pour que vous les retrouviez sur tous vos appareils. Vous pouvez supprimer vous-même votre compte ; vos favoris et votre inscription aux e-mails sont alors supprimés aussi.</p>

      <h2>E-mails</h2>
      <p>Si vous vous inscrivez à nos e-mails, nous conservons votre adresse e-mail, les sujets que vous choisissez ainsi que votre pays et votre langue. Vous confirmez d’abord votre inscription via un lien. Nos e-mails ne contiennent ni pixels de suivi ni liens redirigés servant à mesurer si vous les ouvrez. Vous pouvez vous désinscrire en un clic en bas de chaque e-mail ; nous supprimons alors votre adresse.</p>

      <h2>Contact</h2>
      <p>Si vous nous envoyez un message, nous utilisons votre nom et votre adresse e-mail uniquement pour vous répondre. Nous conservons le message douze mois au maximum.</p>

      <h2>Pinterest, Facebook et Instagram</h2>
      <p>Kleurhoek publie ses propres coloriages sur ses propres comptes Pinterest, Facebook et Instagram. Pour cela, nous relions ces comptes via la connexion officielle (OAuth) de Pinterest et de Meta. Nous conservons les jetons d’accès de cette connexion sous forme chiffrée et ne les utilisons que pour publier des messages et créer des tableaux sur nos propres comptes. Nous ne lisons, ne collectons ni ne conservons aucune donnée sur les autres utilisateurs de ces services, et nous n’utilisons pas cette connexion à des fins publicitaires. Le bouton « Enregistrer sur Pinterest » de notre site est un simple lien : aucun script de Pinterest n’est chargé. La connexion peut être supprimée à tout moment ; nous supprimons alors les jetons.</p>

      <h2>Qui nous aide</h2>
      <p>Le site est hébergé chez Scaleway à Amsterdam. Cloudflare assure la rapidité et la sécurité, Zitadel gère la connexion et Brevo envoie nos e-mails. Ils traitent les données uniquement pour notre compte et uniquement à cette fin. Si vous cliquez sur un lien vers une boutique, comme Amazon, c’est la politique de confidentialité de cette boutique qui s’applique à partir de ce moment.</p>

      <h2>Vos droits</h2>
      <p>Vous pouvez demander quelles données nous détenons sur vous, et les faire rectifier ou supprimer. Pour cela, <Link href={contact("privacy")}>contactez-nous</Link>. Si vous n’êtes pas d’accord avec la façon dont nous traitons vos données, vous pouvez déposer une plainte auprès de l’Autoriteit Persoonsgegevens (l’autorité néerlandaise de protection des données) ou de l’autorité de votre propre pays.</p>

      <h2>Modifications</h2>
      <p>Si quelque chose change dans ce que nous conservons, nous mettons cette page à jour. La date en haut indique quand elle a été mise à jour pour la dernière fois.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Politique de confidentialité", description: "Quelles données Kleurhoek conserve, pourquoi et combien de temps : pas de cookies, un comptage anonyme des visites et des comptes réservés aux adultes.", Body };
