export function getInitData() {
  if (window.Telegram?.WebApp?.initData) {
    return window.Telegram.WebApp.initData;
  }
  return import.meta.env.VITE_MOCK_INIT_DATA || '';
}

export function expandWebApp() {
  window.Telegram?.WebApp?.expand();
  window.Telegram?.WebApp?.ready();
}

export function hapticFeedback(type = 'light') {
  window.Telegram?.WebApp?.HapticFeedback?.impactOccurred(type);
}

export function showBackButton(show = true) {
  if (show) {
    window.Telegram?.WebApp?.BackButton?.show();
  } else {
    window.Telegram?.WebApp?.BackButton?.hide();
  }
}
