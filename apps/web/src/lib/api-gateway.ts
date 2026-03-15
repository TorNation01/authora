/**
 * Modular API gateway compatibility.
 * Standalone: direct to backend (NEXT_PUBLIC_API_URL or same-origin).
 * Anakatech: may route through upstream gateway (API_GATEWAY_URL).
 */

export function getApiBase(): string {
  if (typeof window === 'undefined') return process.env.NEXT_PUBLIC_API_URL || '';
  return process.env.NEXT_PUBLIC_API_URL || '';
}
