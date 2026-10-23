import { Logo } from "@kleurhoek/theme";

export default function LoggedOut() {
  return (
    <div className="kh-login-page">
      <main className="kh-login">
        <Logo size={26} />
        <div><h1>Je bent uitgelogd</h1><p>Tot de volgende keer.</p></div>
        <a className="ui-btn" href="https://www.kleurhoek.nl">Naar Kleurhoek</a>
      </main>
    </div>
  );
}
