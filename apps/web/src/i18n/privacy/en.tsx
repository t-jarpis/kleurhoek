import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Last updated on 2 November 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be and www.kleurhoek.com) is a website with original colouring pages and craft sheets for children. We collect as little as possible. This page sets out exactly what we do keep, why, for how long and what your rights are.</p>

      <h2>Who we are</h2>
      <p>Kleurhoek is a Dutch website. For questions about privacy, please use our <Link href={contact("privacy")}>contact form</Link>.</p>

      <h2>Visiting and colouring</h2>
      <p>We count visits anonymously: without cookies, without IP addresses and without anything that can be traced back to you. We do not use advertising or tracking scripts from anyone else, including Google, Meta or Pinterest. You can colour in, print and colour together without an account. What you colour stays on your own device. When you colour together, the strokes pass through our server to the others in the room, without any names; after 30 minutes without colouring, the room stops. Names you type for gift labels are never sent to our server.</p>

      <h2>Account</h2>
      <p>Accounts are for adults only (16 or older). Children do not need an account and cannot create one. If you have an account, we keep your name, your email address and your favourites, so you can find them on all your devices. You can delete your account yourself; your favourites and email sign-up are deleted with it.</p>

      <h2>Email</h2>
      <p>If you sign up for emails, we keep your email address, the topics you choose and your country and language. You first confirm your sign-up via a link. Our emails contain no tracking pixels or redirected links to measure whether you open them. You can unsubscribe with one click at the bottom of every email, and we then delete your address.</p>

      <h2>Contact</h2>
      <p>If you send us a message, we only use your name and email address to reply to you. We keep the message for no more than twelve months.</p>

      <h2>Pinterest, Facebook and Instagram</h2>
      <p>Kleurhoek publishes its own colouring pages on Kleurhoek&apos;s own accounts on Pinterest, Facebook and Instagram. To do so, we connect those accounts through the official sign-in (OAuth) of Pinterest and Meta. We store the access tokens for that connection encrypted and use them only to publish posts and create boards on our own accounts. We do not read, collect or store data about other users of those services, and we do not use the connection for advertising. The &quot;Save to Pinterest&quot; button on our site is a plain link: no Pinterest script is loaded. The connection can be removed at any time, after which we delete the tokens.</p>

      <h2>Who helps us</h2>
      <p>The website runs at Scaleway in Amsterdam. Cloudflare provides speed and security, Zitadel handles sign-in and Brevo sends our emails. They process data only on our behalf and only for that purpose. If you click a link to a shop, such as Amazon, that shop&apos;s privacy policy applies from then on.</p>

      <h2>Your rights</h2>
      <p>You may ask which data we hold about you, and have it corrected or deleted. Please <Link href={contact("privacy")}>get in touch</Link> to do so. If you disagree with how we handle your data, you can lodge a complaint with the Dutch Data Protection Authority (Autoriteit Persoonsgegevens) or the authority in your own country.</p>

      <h2>Changes</h2>
      <p>If anything changes in what we keep, we update this page. The date at the top shows when it was last updated.</p>
    </>
  );
}

export const en: PrivacyText = { title: "Privacy policy", description: "What data Kleurhoek keeps, why and for how long: no cookies, anonymous visit counts, and accounts for adults only.", Body };
