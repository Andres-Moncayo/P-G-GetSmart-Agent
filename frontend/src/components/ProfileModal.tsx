import React from 'react';
import { useAuthStore } from '../stores/authStore';
import type { UserProfile } from '../types';

interface ProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLogout: () => Promise<void>;
}

export const ProfileModal: React.FC<ProfileModalProps> = ({ isOpen, onClose, onLogout }) => {
  const { user } = useAuthStore();

  if (!isOpen || !user) return null;

  const getAvatarInitials = (name: string): string => {
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  const getRoleBadge = (role: string): string => {
    switch (role) {
      case 'admin':
        return 'Administrator · Enterprise';
      case 'editor':
        return 'Editor · Enterprise';
      case 'viewer':
        return 'Viewer · Enterprise';
      case 'demo':
        return 'Demo User · Limited Access';
      default:
        return 'User · Enterprise';
    }
  };

  const handleLogout = async () => {
    onClose();
    await onLogout();
  };

  const menuItems = [
    { icon: 'fa-user-edit', label: 'Edit profile', action: 'edit-profile' },
    { icon: 'fa-shield-alt', label: 'Security & SSO', action: 'security' },
    { icon: 'fa-sliders-h', label: 'Preferences', action: 'preferences' },
    { icon: 'fa-key', label: 'API Keys', action: 'api-keys' },
  ];

  const bottomMenuItems = [
    { icon: 'fa-question-circle', label: 'Help & Support', action: 'help' },
    { icon: 'fa-sign-out-alt', label: 'Sign out', action: 'logout', isDanger: true },
  ];

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 z-50 bg-black/50"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="fixed top-16 right-6 z-50 w-72 rounded-2xl bg-surface border border-border shadow-modal animate-slide-up">
        {/* User Header */}
        <div className="p-5 border-b border-border">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-accent to-secondary flex items-center justify-center text-white text-lg font-bold">
              {user.avatar_initials || getAvatarInitials(user.name)}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-primary truncate">
                {user.name}
              </h3>
              <p className="text-xs text-muted truncate">
                {user.email}
              </p>
              <div className="mt-2 text-xs text-muted bg-elevated border border-border rounded-lg px-3 py-1.5">
                {getRoleBadge(user.role)}
              </div>
            </div>
          </div>
        </div>
        
        {/* Menu Items */}
        <div className="py-2">
          {menuItems.map((item) => (
            <button
              key={item.action}
              onClick={() => {
                // Handle menu item actions
                console.log(`Action: ${item.action}`);
                onClose();
              }}
              className="w-full flex items-center px-5 py-2.5 text-left hover:bg-elevated transition-all duration-200"
            >
              <i className={`fas ${item.icon} text-muted min-w-[16px]`} />
              <span className="ml-3 text-sm text-secondary hover:text-primary">
                {item.label}
              </span>
            </button>
          ))}
        </div>
        
        {/* Divider */}
        <div className="border-t border-border mx-5 my-2" />
        
        {/* Bottom Menu Items */}
        <div className="py-2">
          {bottomMenuItems.map((item) => (
            <button
              key={item.action}
              onClick={() => {
                if (item.action === 'logout') {
                  handleLogout();
                } else {
                  console.log(`Action: ${item.action}`);
                  onClose();
                }
              }}
              className={`w-full flex items-center px-5 py-2.5 text-left transition-all duration-200 ${
                item.isDanger
                  ? 'text-danger hover:bg-danger/10'
                  : 'text-secondary hover:text-primary hover:bg-elevated'
              }`}
            >
              <i 
                className={`fas ${item.icon} min-w-[16px] ${
                  item.isDanger ? 'text-danger' : 'text-muted'
                }`} 
              />
              <span className={`ml-3 text-sm ${
                item.isDanger ? 'text-danger' : 'text-secondary hover:text-primary'
              }`}>
                {item.label}
              </span>
            </button>
          ))}
        </div>
      </div>
    </>
  );
};