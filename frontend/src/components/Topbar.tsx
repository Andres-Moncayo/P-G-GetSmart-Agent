import React from 'react';
import { useAuthStore } from '../stores/authStore';
import { useUIStore } from '../stores/uiStore';
import { ProfileModal } from './ProfileModal';
import type { SsoProvider } from '../types';

const navItems = [
  { label: 'Reports', path: '/reports' },
  { label: 'Pipeline', path: '/pipeline' },
  { label: 'Templates', path: '/templates' },
  { label: 'Docs', path: '/docs' },
];

export const Topbar: React.FC = () => {
  const { user, logout } = useAuthStore();
  const { profileModalOpen, toggleProfileModal, activeNavItem, setActiveNavItem } = useUIStore();

  const getAvatarInitials = (name: string): string => {
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <>
      <header className="sticky top-0 z-40 h-16 glass border-b border-border">
        <div className="flex h-full items-center justify-between px-6">
          {/* Left section */}
          <div className="flex items-center space-x-8">
            {/* Logo and brand */}
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-secondary flex items-center justify-center">
                <i className="fas fa-gamepad text-white text-sm" />
              </div>
              <h1 className="text-lg font-bold text-primary">
                Get<span className="text-accent">Smart</span>
              </h1>
            </div>
            
            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-1">
              {navItems.map((item) => (
                <button
                  key={item.path}
                  onClick={() => setActiveNavItem(item.path)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    activeNavItem === item.path
                      ? 'bg-elevated text-primary'
                      : 'text-muted hover:text-primary hover:bg-elevated'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </nav>
          </div>
          
          {/* Right section */}
          <div className="flex items-center space-x-3">
            {/* Search icon */}
            <button className="w-9 h-9 flex items-center justify-center bg-surface border border-border rounded-lg hover:bg-elevated transition-all duration-200">
              <i className="fas fa-search text-muted text-sm" />
            </button>
            
            {/* Notifications */}
            <button className="relative w-9 h-9 flex items-center justify-center bg-surface border border-border rounded-lg hover:bg-elevated transition-all duration-200">
              <i className="fas fa-bell text-muted text-sm" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-accent rounded-full animate-pulse-dot" />
            </button>
            
            {/* Profile trigger */}
            <button
              onClick={toggleProfileModal}
              className="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-elevated transition-all duration-200"
            >
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-accent to-secondary flex items-center justify-center text-white text-xs font-bold">
                {user?.avatar_initials || getAvatarInitials(user?.name || 'User')}
              </div>
              <span className="text-sm font-medium text-secondary hidden sm:block">
                {user?.name?.split(' ')[0] || 'User'}
              </span>
              <i className="fas fa-chevron-down text-muted text-xs" />
            </button>
          </div>
        </div>
      </header>
      
      {/* Profile Modal */}
      <ProfileModal 
        isOpen={profileModalOpen}
        onClose={toggleProfileModal}
        onLogout={logout}
      />
    </>
  );
};