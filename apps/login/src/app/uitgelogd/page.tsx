import { Logo } from "@kleurhoek/theme";
import { headers } from "next/headers";
import { pickLanguage, t as messages } from "@/lib/i18n";

export default async function LoggedOut() {
  const t = messages(pickLanguage(undefined, (await headers()).get("accept-language")));
  return (
    <div className="kh-login-page">
      <main className="kh-login">
        <Logo size={26} />
        <div><h1>{t.loggedOutTitle}</h1><p>{t.loggedOutText}</p></div>
        <a className="ui-btn" href="https://www.kleurhoek.nl">{t.toSite}</a>
      </main>
    </div>
  );
}
