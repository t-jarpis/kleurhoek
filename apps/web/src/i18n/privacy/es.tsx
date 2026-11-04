import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Última actualización: 4 de noviembre de 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be y www.kleurhoek.com) es un sitio web con dibujos para colorear y fichas de manualidades propios para niños. Recogemos lo mínimo posible. En esta página explicamos exactamente qué guardamos, por qué, durante cuánto tiempo y cuáles son tus derechos.</p>

      <h2>Quiénes somos</h2>
      <p>Kleurhoek es un sitio web neerlandés. Si tienes preguntas sobre privacidad, usa nuestro <Link href={contact("privacy")}>formulario de contacto</Link>.</p>

      <h2>Visitar y colorear</h2>
      <p>Contamos las visitas de forma anónima: sin cookies, sin direcciones IP y sin nada que pueda llevar hasta ti. No usamos scripts publicitarios ni de seguimiento de terceros, tampoco de Google, Meta ni Pinterest. Puedes colorear, imprimir y colorear en grupo sin cuenta. Lo que coloreas se queda en tu propio dispositivo. Cuando coloreas en grupo, los trazos pasan por nuestro servidor hasta los demás de la sala, sin nombres; tras 30 minutos sin que nadie coloree, la sala se cierra. Los nombres que escribes para las etiquetas de regalo nunca se envían a nuestro servidor.</p>
      <p>Para no contar dos veces a los visitantes, creamos cada día un código a partir de tu dirección IP y tu navegador, con una clave que cambia a diario; la dirección IP en sí no la guardamos. Pasados 90 días sustituimos ese código por uno aleatorio, de modo que ni siquiera nosotros podemos vincular ya un recuento a un dispositivo. Los recuentos en sí (qué página, qué país, móvil u ordenador, cuándo) sí los guardamos, para ver cómo se usa el sitio a lo largo de los años.</p>

      <h2>Cuenta</h2>
      <p>Las cuentas son solo para adultos (16 años o más). Los niños no necesitan cuenta y no pueden crear una. Si tienes cuenta, guardamos tu nombre, tu dirección de correo electrónico y tus favoritos, para que los encuentres en todos tus dispositivos. Puedes eliminar tu cuenta tú mismo; con ella se eliminan también tus favoritos y tu suscripción al correo.</p>

      <h2>Correo electrónico</h2>
      <p>Si te suscribes a nuestros correos, guardamos tu dirección de correo electrónico, los temas que elijas y tu país e idioma. Primero confirmas la suscripción mediante un enlace. Nuestros correos no contienen píxeles de seguimiento ni enlaces redirigidos para medir si los abres. Puedes darte de baja con un clic al final de cada correo, y entonces eliminamos tu dirección.</p>

      <h2>Contacto</h2>
      <p>Si nos envías un mensaje, usamos tu nombre y tu dirección de correo electrónico solo para responderte. Guardamos el mensaje como máximo doce meses.</p>

      <h2>Pinterest, Facebook e Instagram</h2>
      <p>Kleurhoek publica sus propios dibujos para colorear en las cuentas propias de Kleurhoek en Pinterest, Facebook e Instagram. Para ello conectamos esas cuentas mediante el inicio de sesión oficial (OAuth) de Pinterest y Meta. Guardamos cifrados los tokens de acceso de esa conexión y solo los usamos para publicar en nuestras propias cuentas y crear tableros en ellas. No leemos, recopilamos ni guardamos datos de otros usuarios de esos servicios, y no usamos la conexión para publicidad. El botón «Guardar en Pinterest» de nuestro sitio es un enlace normal: no se carga ningún script de Pinterest. La conexión puede eliminarse en cualquier momento, y después borramos los tokens.</p>

      <h2>Quién nos ayuda</h2>
      <p>El sitio web está alojado en Scaleway, en Amsterdam. Cloudflare se encarga de la velocidad y la seguridad, Zitadel del inicio de sesión y Brevo del envío de nuestros correos. Solo tratan datos por encargo nuestro y únicamente para ese fin. Si haces clic en un enlace a una tienda, como Amazon, a partir de ese momento se aplica la política de privacidad de esa tienda.</p>

      <h2>Tus derechos</h2>
      <p>Puedes preguntarnos qué datos tenemos sobre ti y pedir que los corrijamos o eliminemos. Para ello, <Link href={contact("privacy")}>ponte en contacto</Link> con nosotros. Si no estás de acuerdo con cómo tratamos tus datos, puedes presentar una reclamación ante la Autoriteit Persoonsgegevens (la autoridad neerlandesa de protección de datos) o ante la autoridad de tu propio país.</p>

      <h2>Cambios</h2>
      <p>Si cambia algo en lo que guardamos, actualizamos esta página. La fecha de arriba indica cuándo se actualizó por última vez.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Política de privacidad", description: "Qué datos guarda Kleurhoek, por qué y durante cuánto tiempo: sin cookies, recuento anónimo de visitas y cuentas solo para adultos.", Body };
