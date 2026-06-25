export function trimmed(value: string): string {
  return value.trim();
}

export function trimmedOrUndefined(value: string): string | undefined {
  const t = value.trim();
  return t || undefined;
}

export function trimmedOrNull(value: string | null): string | null {
  return value ? value.trim() || null : null;
}