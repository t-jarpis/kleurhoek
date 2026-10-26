import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Portugees (ADR 0026). Zelfde opbouw als nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Última atualização: 24 de outubro de 2026.</p>
      <p>Nesta página contamos o que você pode fazer com os desenhos para colorir e os trabalhos manuais do Kleurhoek, como indicamos links para outros sites e como nos avisar de algo. Ao usar o Kleurhoek, você aceita estas condições.</p>

      <h2>Criações próprias</h2>
      <p>Todos os desenhos para colorir, moldes para recortar e maquetes de papel do Kleurhoek foram feitos especialmente para o Kleurhoek. Nós os criamos com a ajuda de IA e verificamos cada desenho antes de publicá-lo. Não copiamos nada de outros sites nem de livros, e não recriamos personagens, marcas ou figuras conhecidas. O site, o nome Kleurhoek e a coleção de desenhos pertencem ao Kleurhoek.</p>
      <p>Você pode usar os desenhos de graça:</p>
      <ul>
        <li>em casa, para colorir, imprimir e distribuir para a família e os amigos;</li>
        <li>na escola, na creche, em uma associação ou na biblioteca, inclusive em grandes quantidades;</li>
        <li>em uma festa, por exemplo como atividade de trabalhos manuais.</li>
      </ul>
      <p>Sem a nossa autorização por escrito, não é permitido: vender os desenhos (avulsos, em um livrinho ou como download), publicá-los como material próprio em outro site, em um aplicativo ou nas redes sociais, nem usá-los em produtos ou em publicidade. Você pode, sim, compartilhá-los com um link para o desenho no Kleurhoek.</p>

      <h2>Temas dos criadores</h2>
      <p>As crianças muitas vezes procuram desenhos para colorir de personagens de um desenho animado, de um parque de diversões ou de um livro. Esses desenhos pertencem aos seus criadores, e nós não podemos desenhá-los nem copiá-los. Mas muitos criadores os oferecem de graça no próprio site. Em <Link href={link(base, "/themas")}>Temas dos criadores</Link> reunimos links para essas páginas. Para isso, seguimos estas regras:</p>
      <ul>
        <li>Só indicamos links para o site oficial do criador ou do detentor dos direitos, nunca para sites que copiam desenhos de outros.</li>
        <li>Não mostramos imagens, desenhos nem logotipos do criador, e também não os guardamos. No nosso site você vê apenas uma descrição própria e um link. Isso só pode ser diferente se um criador nos der autorização por escrito; nesse caso, informamos isso.</li>
        <li>Verificamos cada link antes de publicá-lo. Depois, um programa de computador confere todos os dias se a página ainda existe. Se uma página desaparecer, removemos o link automaticamente. Sempre respeitamos as regras (robots.txt) do site do criador.</li>
        <li>O conteúdo dos sites dos criadores é de responsabilidade deles e segue as condições deles. Nós não temos nenhum controle sobre ele.</li>
      </ul>
      <p>Você é criador e quer que alteremos ou removamos um link, ou prefere fazer uma parceria com a gente? <Link href={contact("partnership")}>Entre em contato conosco</Link>. Faremos a alteração em até cinco dias úteis.</p>

      <h2>Marcas e nomes</h2>
      <p>Os nomes de personagens, parques de diversões, séries e marcas pertencem aos seus proprietários. Só os usamos para descrever onde você pode encontrar algo. O Kleurhoek não tem vínculo com esses proprietários nem é patrocinado por eles, a não ser que isso esteja indicado expressamente.</p>

      <h2>Links de afiliado</h2>
      <p>Em alguns desenhos e temas mencionamos coisas que você pode usar com eles, como uma tesoura infantil ou lápis de cor. São links de afiliado: se você comprar algo por um deles, a loja paga ao Kleurhoek uma pequena comissão. Você paga o mesmo. Assim os desenhos continuam grátis. Os links de afiliado estão sempre claramente identificados. A loja é responsável pelo produto, pelo preço e pela entrega.</p>

      <h2>Avisos sobre direitos autorais</h2>
      <p>Você acha que há algo no Kleurhoek sobre o qual você tem os direitos, ou que um link leva a algo que não deveria estar lá? Avise-nos pelo <Link href={contact("copyright")}>formulário de contato</Link> com o assunto &quot;Direitos autorais&quot;. Informe de qual página se trata, por que você acha que não está certo e como podemos falar com você. Respondemos em até cinco dias úteis e, se houver motivo, retiramos o conteúdo enquanto investigamos.</p>

      <h2>Trabalhos manuais com segurança</h2>
      <p>Os moldes para recortar e as maquetes de papel foram pensados para serem feitos junto com um adulto. Use uma tesoura infantil e, nas lanternas de papel, sempre uma luzinha de LED, nunca uma vela de verdade. As peças pequenas não são adequadas para crianças com menos de três anos.</p>

      <h2>Responsabilidade</h2>
      <p>Fazemos o Kleurhoek com muito cuidado, mas não podemos prometer que tudo esteja sempre livre de erros nem que o site esteja sempre disponível. Na medida em que a lei permitir, o Kleurhoek não se responsabiliza por danos decorrentes do uso do site, dos desenhos ou dos sites para os quais indicamos links.</p>

      <h2>Privacidade</h2>
      <p>Contamos as visitas de forma anônima: sem cookies, sem endereço IP e sem nada que permita identificar você. Para colorir ou imprimir, você não precisa de uma conta. Se criar uma, guardamos seu nome, seu e-mail e seus favoritos, para que você os encontre em todos os seus dispositivos; você mesmo pode excluir sua conta quando quiser. Se você se inscrever nos e-mails, usamos seu endereço só para isso, e o apagamos quando você cancelar. Se você nos enviar uma mensagem, usamos seu nome e seu e-mail apenas para responder e guardamos a mensagem por no máximo doze meses. Quer que apaguemos sua mensagem antes disso? <Link href={contact("privacy")}>É só nos dizer</Link>.</p>

      <h2>Alterações e perguntas</h2>
      <p>Podemos alterar este aviso legal, por exemplo quando acrescentarmos algo novo ao Kleurhoek. No topo da página está indicado quando ele foi atualizado pela última vez. Este aviso legal é regido pela legislação dos Países Baixos. Tem alguma pergunta? <Link href={contact()}>Entre em contato conosco</Link>.</p>
    </>
  );
}
