import { Global, Injectable, Logger, Module } from "@nestjs/common";

/**
 * Domeinevents (ADR 0066): een domein meldt wat er gebeurd is, andere domeinen reageren zonder dat de melder ze
 * kent. In het proces zelf en na de transactie van de melder. Nieuwe events hier toevoegen, met wie ze stuurt.
 */
export interface DomainEventMap {
  /** Identity, vlak voordat een websiteaccount verdwijnt: elk domein ruimt zijn gegevens van deze gebruiker op. */
  "identity.account.deleted": { userId: string };
  /** Catalogus, na het starten: platen die nieuw zijn of een nieuwe versie kregen. */
  "catalog.plates.published": { added: string[]; changed: string[] };
}
export type DomainEventName = keyof DomainEventMap;
type Handler<K extends DomainEventName> = (payload: DomainEventMap[K]) => Promise<void> | void;

@Injectable()
export class DomainEvents {
  private readonly log = new Logger("DomainEvents");
  private readonly handlers = new Map<DomainEventName, { who: string; fn: Handler<never> }[]>();

  /** Reageren op een event. `who` is het domein, voor de logs. */
  on<K extends DomainEventName>(name: K, who: string, fn: Handler<K>) {
    this.handlers.set(name, [...(this.handlers.get(name) ?? []), { who, fn: fn as Handler<never> }]);
  }

  /**
   * Alle reacties uitvoeren, na elkaar. `strict`: één mislukte reactie laat het geheel mislukken (bijvoorbeeld bij
   * het verwijderen van een account: liever opnieuw proberen dan gegevens laten staan). Anders alleen loggen.
   */
  async emit<K extends DomainEventName>(name: K, payload: DomainEventMap[K], opts: { strict?: boolean } = {}) {
    const errors: unknown[] = [];
    for (const h of this.handlers.get(name) ?? []) {
      try { await (h.fn as Handler<K>)(payload); } catch (e) {
        this.log.error(`${name} → ${h.who}: ${e}`);
        errors.push(e);
      }
    }
    if (opts.strict && errors.length) throw new AggregateError(errors, `${name}: ${errors.length} reactie(s) mislukt`);
  }

  /** Voor tests en het contract: wie reageert op wat. */
  listeners(name: DomainEventName): string[] { return (this.handlers.get(name) ?? []).map((h) => h.who); }
}

@Global()
@Module({ providers: [DomainEvents], exports: [DomainEvents] })
export class EventsModule {}
