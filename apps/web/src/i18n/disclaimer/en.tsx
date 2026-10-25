import Link from "next/link";
import type { DisclaimerProps } from "./types";

/** Disclaimer in British English (ADR 0026). Same structure as nl.tsx. */
export function Disclaimer({ market, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Last updated on 24 October 2026.</p>
      <p>This page explains what you may do with Kleurhoek&apos;s colouring pages and craft sheets, how we link to other websites and how to report something to us. By using Kleurhoek, you agree to these terms.</p>

      <h2>Our own designs</h2>
      <p>All colouring pages, cut-outs and paper models on Kleurhoek are made especially for Kleurhoek. We create them with the help of AI and check every page before it goes online. We don&apos;t copy anything from other websites or from books, and we don&apos;t recreate well-known characters, brands or figures. The website, the Kleurhoek name and the collection of pages belong to Kleurhoek.</p>
      <p>You may use the pages free of charge:</p>
      <ul>
        <li>at home, to colour in, print and hand out to family and friends;</li>
        <li>at school, at nursery, at a club or in the library, including in large numbers;</li>
        <li>at a party, for example as a craft activity.</li>
      </ul>
      <p>The following is not allowed without our written permission: selling the pages (individually, in a booklet or as a download), putting them on another website, in an app or on social media as your own material, or using them in products or advertising. You are welcome to share a link to the page on Kleurhoek.</p>

      <h2>Themes from the makers</h2>
      <p>Children often look for colouring pages of characters from a cartoon, a theme park or a book. Those drawings belong to their makers, and we are not allowed to make or copy them ourselves. But many makers offer them for free on their own websites. Under <Link href={`/${market}/themas`}>Themes from the makers</Link> we collect links to those pages. The following applies:</p>
      <ul>
        <li>We only link to the official website of the maker or rights holder, never to sites that copy other people&apos;s drawings.</li>
        <li>We don&apos;t show or store any images, drawings or logos of the maker. All you see on our site is our own description and a link. This may be different only if a maker gives us written permission, in which case we say so.</li>
        <li>We check every link before it goes online. After that, a computer program checks every day whether the page still exists. If a page disappears, we remove the link automatically. In doing so, we always follow the rules (robots.txt) of the maker&apos;s website.</li>
        <li>The content of makers&apos; websites is their own responsibility and subject to their own terms. We have no control over it.</li>
      </ul>
      <p>Are you a maker and would you like us to change or remove a link, or would you like to work with us? <Link href={contact("partnership")}>Get in touch with us</Link>. We will make the change within five working days.</p>

      <h2>Brands and names</h2>
      <p>Names of characters, theme parks, series and brands belong to their owners. We only use them to describe where you can find something. Kleurhoek is not affiliated with these owners and is not sponsored by them, unless this is explicitly stated.</p>

      <h2>Partner links</h2>
      <p>With some pages and themes, we mention things you can use with them, such as children&apos;s scissors or colouring pencils. These are partner links: if you buy something through such a link, Kleurhoek receives a small fee from the shop. You pay the same. That&apos;s how we keep the pages free. Partner links are always clearly marked. The shop is responsible for the product, the price and the delivery.</p>

      <h2>Reporting copyright</h2>
      <p>Do you think there is something on Kleurhoek that you hold the rights to, or that a link points to something it shouldn&apos;t? Report it using the <Link href={contact("copyright")}>contact form</Link> with the subject &quot;Copyright&quot;. Tell us which page it concerns, why you think it isn&apos;t right and how we can reach you. We will respond within five working days and, if there is reason to, remove it while we look into it.</p>

      <h2>Crafting safely</h2>
      <p>Cut-outs and paper models are meant to be made together with an adult. Use children&apos;s scissors and, for lanterns, always use an LED light and never a real candle. Small parts are not suitable for children under three.</p>

      <h2>Liability</h2>
      <p>We make Kleurhoek with great care, but we cannot promise that everything is always free of errors or that the website is always available. To the extent permitted by law, Kleurhoek is not liable for any damage resulting from the use of the website, the pages or the websites we link to.</p>

      <h2>Privacy</h2>
      <p>We count visits anonymously: without cookies, without IP addresses and without anything that can be traced back to you. You don&apos;t need an account to colour in or print. If you do create one, we keep your name, your email address and your favourites, so you can find them on all your devices; you can delete your account yourself at any time. If you sign up for emails, we only use your address for that, and unsubscribing deletes it. If you send us a message, we only use your name and email address to reply to you, and we keep the message for no more than twelve months. Would you like us to delete your message sooner? <Link href={contact("privacy")}>Let us know</Link>.</p>

      <h2>Changes and questions</h2>
      <p>We may change this disclaimer, for example when something new is added to Kleurhoek. The date at the top shows when it was last updated. This disclaimer is governed by Dutch law. Questions? <Link href={contact()}>Get in touch with us</Link>.</p>
    </>
  );
}
