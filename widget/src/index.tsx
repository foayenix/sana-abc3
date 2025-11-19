import React from 'react';
import { createRoot } from 'react-dom/client';
import { BookingWidget } from './components/BookingWidget';
import './styles/widget.css';

interface SANAWidgetConfig {
  key: string;
  container: string;
  practitionerId?: string;
  theme?: 'light' | 'dark';
  primaryColor?: string;
  onBookingComplete?: (booking: any) => void;
  onError?: (error: any) => void;
}

declare global {
  interface Window {
    SANAWidget: {
      init: (config: SANAWidgetConfig) => void;
      destroy: () => void;
    };
  }
}

let widgetRoot: ReturnType<typeof createRoot> | null = null;

window.SANAWidget = {
  init: (config: SANAWidgetConfig) => {
    const container = document.querySelector(config.container);
    if (!container) {
      console.error(`SANA Widget: Container "${config.container}" not found`);
      return;
    }

    widgetRoot = createRoot(container);
    widgetRoot.render(
      <React.StrictMode>
        <BookingWidget
          widgetKey={config.key}
          practitionerId={config.practitionerId}
          theme={config.theme || 'light'}
          primaryColor={config.primaryColor || '#345519'}
          onBookingComplete={config.onBookingComplete}
          onError={config.onError}
        />
      </React.StrictMode>
    );
  },

  destroy: () => {
    if (widgetRoot) {
      widgetRoot.unmount();
      widgetRoot = null;
    }
  },
};

// Auto-init if data attributes are present
document.addEventListener('DOMContentLoaded', () => {
  const autoInitElement = document.querySelector('[data-sana-widget]');
  if (autoInitElement) {
    const key = autoInitElement.getAttribute('data-sana-key');
    if (key) {
      window.SANAWidget.init({
        key,
        container: '[data-sana-widget]',
        theme: (autoInitElement.getAttribute('data-sana-theme') as 'light' | 'dark') || 'light',
        primaryColor: autoInitElement.getAttribute('data-sana-color') || '#345519',
      });
    }
  }
});
