import { getInitData } from '../utils/telegram';

const BASE = import.meta.env.VITE_API_URL || '/api';

export async function api(path, options = {}) {
  const { method = 'GET', body, params } = options;

  let url = `${BASE}${path}`;
  if (params) {
    url += '?' + new URLSearchParams(params).toString();
  }

  const headers = {
    'X-Init-Data': getInitData(),
  };

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }

  const res = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return null;
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  const contentType = res.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return res.json();
  }
  return null;
}
