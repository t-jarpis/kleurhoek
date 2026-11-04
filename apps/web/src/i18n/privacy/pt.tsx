import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Atualizado em 4 de novembro de 2026.</p>
      <p>A Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be e www.kleurhoek.com) é um site com desenhos para colorir e atividades de artesanato próprios para crianças. Coletamos o mínimo possível. Nesta página explicamos exatamente o que guardamos, por que, por quanto tempo e quais são os seus direitos.</p>

      <h2>Quem somos</h2>
      <p>A Kleurhoek é um site holandês. Para dúvidas sobre privacidade, use o nosso <Link href={contact("privacy")}>formulário de contato</Link>.</p>

      <h2>Visitar e colorir</h2>
      <p>Contamos as visitas de forma anônima: sem cookies, sem endereços IP e sem nada que possa ser associado a você. Não usamos scripts de publicidade ou rastreamento de terceiros, nem do Google, da Meta ou do Pinterest. Você pode colorir, imprimir e colorir junto com outras pessoas sem conta. O que você colore fica no seu próprio dispositivo. Quando você colore junto com outras pessoas, os traços passam pelo nosso servidor até os outros participantes da sala, sem nomes; depois de 30 minutos sem ninguém colorir, a sala é encerrada. Os nomes que você digita para etiquetas de presente nunca são enviados ao nosso servidor.</p>
      <p>Para não contar os visitantes duas vezes, criamos a cada dia um código a partir do seu endereço IP e do seu navegador, com uma chave que muda todos os dias; o endereço IP em si não é armazenado. Depois de 90 dias, substituímos esse código por um aleatório, de modo que nem nós conseguimos mais associar uma contagem a um dispositivo. Guardamos as contagens em si (qual página, qual país, celular ou computador, quando) para ver como o site é usado ao longo dos anos.</p>

      <h2>Conta</h2>
      <p>As contas são só para adultos (16 anos ou mais). As crianças não precisam de conta e não podem criar uma. Se você tem uma conta, guardamos o seu nome, o seu endereço de e-mail e os seus favoritos, para que você os encontre em todos os seus dispositivos. Você mesmo pode excluir a sua conta; junto com ela são excluídos os seus favoritos e a sua inscrição nos e-mails.</p>

      <h2>E-mail</h2>
      <p>Se você se inscrever nos nossos e-mails, guardamos o seu endereço de e-mail, os temas que você escolher e o seu país e idioma. Primeiro você confirma a inscrição por meio de um link. Nossos e-mails não contêm pixels de rastreamento nem links redirecionados para medir se você os abre. Você pode cancelar a inscrição com um clique no final de cada e-mail, e então excluímos o seu endereço.</p>

      <h2>Contato</h2>
      <p>Se você nos enviar uma mensagem, usamos o seu nome e endereço de e-mail apenas para responder. Guardamos a mensagem por no máximo doze meses.</p>

      <h2>Pinterest, Facebook e Instagram</h2>
      <p>A Kleurhoek publica os próprios desenhos para colorir nas contas da própria Kleurhoek no Pinterest, no Facebook e no Instagram. Para isso, conectamos essas contas pelo login oficial (OAuth) do Pinterest e da Meta. Guardamos os tokens de acesso dessa conexão de forma criptografada e só os usamos para publicar posts e criar pastas nas nossas próprias contas. Não lemos, coletamos nem guardamos dados de outros usuários desses serviços, e não usamos a conexão para publicidade. O botão “Salvar no Pinterest” no nosso site é um link comum: nenhum script do Pinterest é carregado. A conexão pode ser removida a qualquer momento, e depois disso excluímos os tokens.</p>

      <h2>Quem nos ajuda</h2>
      <p>O site fica hospedado na Scaleway, em Amsterdam. A Cloudflare cuida da velocidade e da segurança, o Zitadel do login e a Brevo do envio dos nossos e-mails. Eles tratam dados apenas em nosso nome e só para essa finalidade. Se você clicar em um link para uma loja, como a Amazon, a partir desse momento vale a política de privacidade dessa loja.</p>

      <h2>Seus direitos</h2>
      <p>Você pode perguntar quais dados temos sobre você e pedir que sejam corrigidos ou excluídos. Para isso, <Link href={contact("privacy")}>entre em contato</Link> conosco. Se não concordar com a forma como tratamos os seus dados, você pode apresentar uma reclamação à Autoriteit Persoonsgegevens (a autoridade holandesa de proteção de dados) ou à autoridade do seu próprio país.</p>

      <h2>Alterações</h2>
      <p>Se algo mudar no que guardamos, atualizamos esta página. A data no topo mostra quando ela foi atualizada pela última vez.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Política de privacidade", description: "Quais dados a Kleurhoek guarda, por que e por quanto tempo: sem cookies, contagem anônima de visitas e contas só para adultos.", Body };
