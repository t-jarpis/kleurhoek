export const metadata = { title: "Uitgelogd" };

export default function LoggedOut() {
  return (
    <div className="center">
      <h1>Je bent uitgelogd</h1>
      <p className="lead">Ook bij Zitadel. Sluit het venster als je op een gedeelde computer werkt.</p>
      <p><a className="button" href="/auth/login">Opnieuw inloggen</a></p>
    </div>
  );
}
