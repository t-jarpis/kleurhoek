import type { OrgKind } from "@/lib/api";

export const KIND_LABEL: Record<OrgKind, string> = {
  platform: "Kleurhoek", school: "School", opvang: "Kinderopvang", vereniging: "Vereniging", bedrijf: "Bedrijf", overig: "Overig",
};

export const back = (path: string, kind: "melding" | "fout", text: string) => `${path}${path.includes("?") ? "&" : "?"}${kind}=${encodeURIComponent(text)}`;
