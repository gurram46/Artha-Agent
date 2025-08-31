'use client';

import React, { useState } from 'react';
import LoginForm from './LoginForm';
import SignupForm from './SignupForm';

interface AuthModalProps {
  onAuthSuccess: (userData: any) => void;
  onClose: () => void;
  initialMode?: 'login' | 'signup';
}

export default function AuthModal({ onAuthSuccess, onClose, initialMode = 'login' }: AuthModalProps) {
  const [mode, setMode] = useState<'login' | 'signup'>(initialMode);

  const handleSwitchToLogin = () => {
    setMode('login');
  };

  const handleSwitchToSignup = () => {
    setMode('signup');
  };

  if (mode === 'login') {
    return (
      <LoginForm
        onLoginSuccess={onAuthSuccess}
        onClose={onClose}
        onSwitchToSignup={handleSwitchToSignup}
      />
    );
  }

  return (
    <SignupForm
      onSignupSuccess={onAuthSuccess}
      onClose={onClose}
      onSwitchToLogin={handleSwitchToLogin}
    />
  );
}