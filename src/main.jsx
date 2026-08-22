import React from 'react';
import { createRoot } from 'react-dom/client';

function VersionBadge() {
  return (
    <div
      style={{
        position: 'fixed',
        bottom: '10px',
        left: '14px',
        fontSize: '10px',
        fontWeight: 600,
        color: '#9AA0B8',
        opacity: 0.75,
        pointerEvents: 'none',
        zIndex: 5,
        letterSpacing: '.03em',
      }}
    >
      Nexus CRM · v1.1 · React + Vite
    </div>
  );
}

createRoot(document.getElementById('react-root')).render(<VersionBadge />);
