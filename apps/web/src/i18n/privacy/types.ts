import type { ComponentType } from "react";

/** Elke taalversie van het privacybeleid: titel, omschrijving en de tekst zelf (ADR 0069). */
export interface PrivacyProps { contact: (topic?: string) => string }
export interface PrivacyText { title: string; description: string; Body: ComponentType<PrivacyProps> }
