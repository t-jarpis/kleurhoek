import Link from "next/link";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Spaans (ADR 0026). Zelfde opbouw als nl.tsx. */
export function Disclaimer({ market, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Última actualización: 24 de octubre de 2026.</p>
      <p>En esta página te contamos qué puedes hacer con los dibujos para colorear y las manualidades de Kleurhoek, cómo enlazamos a otras webs y cómo avisarnos de algo. Al usar Kleurhoek aceptas estas condiciones.</p>

      <h2>Diseños propios</h2>
      <p>Todos los dibujos para colorear, recortables y maquetas de papel de Kleurhoek están hechos especialmente para Kleurhoek. Los creamos con ayuda de IA y revisamos cada dibujo antes de publicarlo. No copiamos nada de otras webs ni de libros, y no recreamos personajes, marcas ni figuras conocidas. La web, el nombre Kleurhoek y la colección de dibujos pertenecen a Kleurhoek.</p>
      <p>Puedes usar los dibujos gratis:</p>
      <ul>
        <li>en casa, para colorearlos, imprimirlos y repartirlos entre familiares y amigos;</li>
        <li>en el colegio, en la guardería, en una asociación o en la biblioteca, también en grandes cantidades;</li>
        <li>en una fiesta, por ejemplo como actividad de manualidades.</li>
      </ul>
      <p>Sin nuestro permiso por escrito no está permitido: vender los dibujos (sueltos, en un cuadernillo o como descarga), publicarlos como material propio en otra web, en una app o en redes sociales, ni usarlos en productos o en publicidad. Sí puedes compartirlos con un enlace al dibujo en Kleurhoek.</p>

      <h2>Temas de sus creadores</h2>
      <p>Los niños suelen buscar dibujos para colorear de personajes de una película de dibujos, de un parque de atracciones o de un libro. Esos dibujos son de sus creadores y nosotros no podemos dibujarlos ni copiarlos. Pero muchos creadores los ofrecen gratis en su propia web. En <Link href={`/${market}/themas`}>Temas de sus creadores</Link> reunimos enlaces a esas páginas. Para ello seguimos estas reglas:</p>
      <ul>
        <li>Solo enlazamos a la web oficial del creador o del titular de los derechos, nunca a webs que copian dibujos de otros.</li>
        <li>No mostramos imágenes, dibujos ni logotipos del creador, ni los guardamos. En nuestra web solo ves una descripción propia y un enlace. Solo puede ser de otra manera si un creador nos da su permiso por escrito; en ese caso lo indicamos.</li>
        <li>Revisamos cada enlace antes de publicarlo. Después, un programa informático comprueba cada día si la página sigue existiendo. Si una página desaparece, quitamos el enlace automáticamente. Siempre respetamos las reglas (robots.txt) de la web del creador.</li>
        <li>El contenido de las webs de los creadores es responsabilidad suya y se rige por sus propias condiciones. Nosotros no tenemos ningún control sobre él.</li>
      </ul>
      <p>¿Eres creador y quieres que cambiemos o quitemos un enlace, o prefieres colaborar con nosotros? <Link href={contact("partnership")}>Ponte en contacto con nosotros</Link>. Lo cambiaremos en un plazo de cinco días laborables.</p>

      <h2>Marcas y nombres</h2>
      <p>Los nombres de personajes, parques de atracciones, series y marcas pertenecen a sus propietarios. Solo los usamos para describir dónde puedes encontrar algo. Kleurhoek no está vinculado a estos propietarios ni patrocinado por ellos, salvo que se indique expresamente.</p>

      <h2>Enlaces de afiliado</h2>
      <p>En algunos dibujos y temas mencionamos cosas que puedes usar con ellos, como unas tijeras infantiles o lápices de colores. Son enlaces de afiliado: si compras algo a través de uno de ellos, la tienda le da a Kleurhoek una pequeña comisión. Tú pagas lo mismo. Así los dibujos siguen siendo gratis. Los enlaces de afiliado siempre están claramente señalados. La tienda es responsable del producto, del precio y de la entrega.</p>

      <h2>Avisos sobre derechos de autor</h2>
      <p>¿Crees que en Kleurhoek hay algo sobre lo que tú tienes los derechos, o que un enlace lleva a algo que no debería estar ahí? Avísanos a través del <Link href={contact("copyright")}>formulario de contacto</Link> con el asunto &quot;Derechos de autor&quot;. Indica de qué página se trata, por qué crees que no es correcto y cómo podemos contactarte. Respondemos en un plazo de cinco días laborables y, si hay motivo para ello, retiramos el contenido mientras lo investigamos.</p>

      <h2>Manualidades seguras</h2>
      <p>Los recortables y las maquetas de papel están pensados para hacerlos junto con un adulto. Usa unas tijeras infantiles y, en los farolillos, siempre una lucecita LED y nunca una vela de verdad. Las piezas pequeñas no son adecuadas para menores de tres años.</p>

      <h2>Responsabilidad</h2>
      <p>Hacemos Kleurhoek con mucho cuidado, pero no podemos prometer que todo esté siempre libre de errores ni que la web esté siempre disponible. En la medida en que la ley lo permita, Kleurhoek no se hace responsable de los daños derivados del uso de la web, de los dibujos o de las webs a las que enlazamos.</p>

      <h2>Privacidad</h2>
      <p>Contamos las visitas de forma anónima: sin cookies, sin dirección IP y sin nada que permita identificarte. Para colorear o imprimir no necesitas una cuenta. Si creas una, guardamos tu nombre, tu correo electrónico y tus favoritos, para que los encuentres en todos tus dispositivos; puedes borrar tu cuenta tú mismo cuando quieras. Si te suscribes a los correos, solo usamos tu dirección para eso, y al darte de baja la borramos. Si nos envías un mensaje, solo usamos tu nombre y tu correo electrónico para responderte y guardamos el mensaje como máximo doce meses. ¿Quieres que borremos tu mensaje antes? <Link href={contact("privacy")}>Dínoslo</Link>.</p>

      <h2>Cambios y preguntas</h2>
      <p>Podemos modificar este aviso legal, por ejemplo cuando añadamos algo nuevo a Kleurhoek. Arriba se indica cuándo se actualizó por última vez. Este aviso legal se rige por la legislación neerlandesa. ¿Tienes preguntas? <Link href={contact()}>Ponte en contacto con nosotros</Link>.</p>
    </>
  );
}
