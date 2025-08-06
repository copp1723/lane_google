import React from 'react';
import { AlertCircle, RefreshCw, Home } from 'lucide-react';

const ErrorView = ({ error, resetError }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '400px',
      padding: '2rem',
      textAlign: 'center'
    }}>
      <AlertCircle size={48} style={{ color: '#ef4444', marginBottom: '1rem' }} />
      <h2 style={{ color: '#111827', marginBottom: '0.5rem', fontSize: '1.5rem', fontWeight: '600' }}>
        Something went wrong
      </h2>
      <p style={{ color: '#6b7280', marginBottom: '2rem', maxWidth: '500px' }}>
        {error?.message || 'We encountered an error loading this page. Please try refreshing or return to the dashboard.'}
      </p>
      <div style={{ display: 'flex', gap: '1rem' }}>
        <button
          onClick={() => window.location.reload()}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontSize: '0.875rem',
            fontWeight: '500'
          }}
        >
          <RefreshCw size={16} />
          Refresh Page
        </button>
        <button
          onClick={() => window.location.href = '/'}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            background: 'transparent',
            color: '#6b7280',
            border: '1px solid #d1d5db',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontSize: '0.875rem',
            fontWeight: '500'
          }}
        >
          <Home size={16} />
          Go to Dashboard
        </button>
      </div>
    </div>
  );
};

export default ErrorView;