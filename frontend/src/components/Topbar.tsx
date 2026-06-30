import React, { useRef, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useUIStore } from '../stores/uiStore';


const menuItems = [
  { icon: 'fa-user-edit',       label: 'Edit profile' },
  { icon: 'fa-shield-alt',      label: 'Security & SSO' },
  { icon: 'fa-sliders-h',       label: 'Preferences' },
  { icon: 'fa-key',             label: 'API Keys' },
];

export const Topbar: React.FC = () => {
  const { user, logout } = useAuthStore();
  const { profileModalOpen, toggleProfileModal } = useUIStore();
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    if (!profileModalOpen) return;
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        toggleProfileModal();
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [profileModalOpen, toggleProfileModal]);

  const initials = (name: string) => {
    const parts = name.trim().split(' ');
    return parts.length >= 2
      ? `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
      : name.slice(0, 2).toUpperCase();
  };

  const getRoleBadge = (role: string) => {
    const map: Record<string, string> = {
      admin: 'Administrator · Enterprise',
      editor: 'Editor · Enterprise',
      viewer: 'Viewer · Enterprise',
      demo: 'Demo User · Limited Access',
    };
    return map[role] ?? 'User · Enterprise';
  };

  const handleLogout = async () => {
    toggleProfileModal();
    await logout();
  };

  return (
    <header className="sticky top-0 z-40 h-16 glass border-b border-border">
      <div className="w-full flex h-full items-center justify-between px-6">

        {/* Left */}
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2.5">
            <img src="/logo.svg" alt="GetSmart Logo" className="w-8 h-8 drop-shadow-[0_0_8px_rgba(99,102,241,0.4)]" />
            <h1 className="text-lg font-bold text-primary">
              Get<span className="text-accent">Smart</span>
            </h1>
          </div>

        </div>

        {/* Right */}
        <div className="flex items-center gap-3">
          <button className="relative w-9 h-9 flex items-center justify-center bg-surface border border-border rounded-lg hover:bg-elevated transition-all">
            <i className="fas fa-bell text-muted text-sm" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-accent dot-pulse" />
          </button>

          {/* Profile button + dropdown (relative container) */}
          <div ref={dropdownRef} className="relative">
            <button
              onClick={toggleProfileModal}
              className="flex items-center gap-2.5 pl-2 pr-3 py-1.5 rounded-xl bg-surface border border-border hover:border-border-hover transition-all"
            >
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-accent to-secondary flex items-center justify-center text-white text-xs font-bold">
                {user?.avatar_initials || initials(user?.name || 'U')}
              </div>
              <span className="text-sm font-medium text-primary-muted hidden sm:block">
                {user?.name?.split(' ')[0] || 'User'}
              </span>
              <i className={`fas fa-chevron-down text-muted text-xs transition-transform duration-200 ${profileModalOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Dropdown */}
            {profileModalOpen && (
              <div className="absolute top-full right-0 mt-2 w-72 rounded-2xl bg-surface border border-border shadow-modal overflow-hidden slide-up z-50">
                {/* User info */}
                <div className="p-5 border-b border-border">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-accent to-secondary flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
                      {user?.avatar_initials || initials(user?.name || 'U')}
                    </div>
                    <div className="min-w-0">
                      <p className="font-semibold text-primary truncate">{user?.name}</p>
                      <p className="text-xs text-muted truncate">{user?.email}</p>
                    </div>
                  </div>
                  <div className="mt-3 px-3 py-1.5 rounded-lg bg-elevated border border-border">
                    <p className="text-xs text-muted">{getRoleBadge(user?.role || '')}</p>
                  </div>
                </div>

                {/* Menu */}
                <div className="py-2">
                  {menuItems.map(item => (
                    <button
                      key={item.label}
                      onClick={toggleProfileModal}
                      className="w-full flex items-center gap-3 px-5 py-2.5 text-left text-sm text-primary-muted hover:text-primary hover:bg-elevated transition-all"
                    >
                      <i className={`fas ${item.icon} text-muted w-4`} />
                      {item.label}
                    </button>
                  ))}

                  <div className="border-t border-border my-2" />

                  <button
                    onClick={toggleProfileModal}
                    className="w-full flex items-center gap-3 px-5 py-2.5 text-left text-sm text-primary-muted hover:text-primary hover:bg-elevated transition-all"
                  >
                    <i className="fas fa-question-circle text-muted w-4" />
                    Help & Support
                  </button>

                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-5 py-2.5 text-left text-sm text-danger hover:bg-danger/10 transition-all"
                  >
                    <i className="fas fa-sign-out-alt w-4" />
                    Sign out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
