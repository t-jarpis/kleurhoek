import { Inject, Injectable, Logger } from "@nestjs/common";
import { createTransport, type Transporter } from "nodemailer";
import { ENV, type Env } from "../../config/env";

export interface OutgoingMail {
  to: string; subject: string; html: string; text: string;
  /** Afmelden met één klik (RFC 8058); niet bij transactionele mail. */
  unsubscribeUrl?: string | undefined;
  transactional: boolean;
}

/**
 * Afleveren (ADR 0037): alles wat we zelf doen eindigt hier, bij SMTP. Welke dienst erachter zit (lokaal Mailpit,
 * een relay, later eventueel een eigen mailserver) is alleen configuratie. Zonder SMTP staat versturen uit.
 */
export const MAIL_TRANSPORT = Symbol("MAIL_TRANSPORT");
export interface MailTransport {
  /** Kan er verstuurd worden (bulk of transactioneel)? */
  enabled(transactional: boolean): boolean;
  send(mail: OutgoingMail): Promise<{ messageId: string }>;
}

@Injectable()
export class SmtpTransport implements MailTransport {
  private readonly log = new Logger("Mail");
  private readonly bulk: Transporter | null;
  private readonly transactional: Transporter | null;

  constructor(@Inject(ENV) private readonly env: Env) {
    // Opties zoals pool staan in de URL (?pool=true&maxConnections=3).
    const make = (url: string | undefined) => (url ? createTransport(url) : null);
    this.bulk = make(env.MAIL_SMTP_URL);
    this.transactional = make(env.MAIL_TRANSACTIONAL_SMTP_URL) ?? this.bulk;
    if (!this.bulk && !this.transactional) this.log.warn("Geen MAIL_SMTP_URL: mails blijven in de wachtrij staan");
  }

  enabled(transactional: boolean) { return Boolean(transactional ? this.transactional : this.bulk); }

  async send(mail: OutgoingMail) {
    const t = mail.transactional ? this.transactional : this.bulk;
    if (!t) throw new Error("Versturen staat uit");
    const info = await t.sendMail({
      from: this.env.MAIL_FROM, to: mail.to, subject: mail.subject, html: mail.html, text: mail.text,
      headers: mail.unsubscribeUrl ? { "List-Unsubscribe": `<${mail.unsubscribeUrl}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" } : {},
    });
    return { messageId: String(info.messageId ?? "") };
  }
}

/** Voor tests: houdt verstuurde mails bij. */
export class MemoryTransport implements MailTransport {
  readonly sent: OutgoingMail[] = [];
  constructor(private readonly on = true) {}
  enabled() { return this.on; }
  async send(mail: OutgoingMail) { this.sent.push(mail); return { messageId: `test-${this.sent.length}` }; }
}
