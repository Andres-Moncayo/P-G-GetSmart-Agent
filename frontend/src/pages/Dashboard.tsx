import React from 'react';

export const Dashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-primary mb-2">Dashboard</h2>
          <p className="text-muted">Welcome to GetSmart - Game Intelligence Library</p>
        </div>
        
        {/* Example content cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-primary">Recent Reports</h3>
              <i className="fas fa-chart-line text-accent" />
            </div>
            <p className="text-muted mb-4">View your latest game analysis reports</p>
            <button className="text-accent hover:text-accent-light text-sm font-medium">
              View all →
            </button>
          </div>
          
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-primary">Pipeline Status</h3>
              <i className="fas fa-tasks text-secondary" />
            </div>
            <p className="text-muted mb-4">Monitor data processing pipelines</p>
            <button className="text-accent hover:text-accent-light text-sm font-medium">
              View pipeline →
            </button>
          </div>
          
          <div className="bg-surface border border-border rounded-xl p-6 shadow-card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-primary">Templates</h3>
              <i className="fas fa-layer-group text-success" />
            </div>
            <p className="text-muted mb-4">Browse report templates and examples</p>
            <button className="text-accent hover:text-accent-light text-sm font-medium">
              Browse templates →
            </button>
          </div>
        </div>
        
        {/* Additional content */}
        <div className="mt-8 bg-surface border border-border rounded-xl p-6 shadow-card">
          <h3 className="text-lg font-semibold text-primary mb-4">Quick Start Guide</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-secondary mb-2">1. Upload Game Data</h4>
              <p className="text-sm text-muted mb-4">Import your game analytics and performance data in various formats.</p>
            </div>
            <div>
              <h4 className="font-medium text-secondary mb-2">2. Generate Reports</h4>
              <p className="text-sm text-muted mb-4">Create intelligent reports using our AI-powered analysis engine.</p>
            </div>
            <div>
              <h4 className="font-medium text-secondary mb-2">3. Share Insights</h4>
              <p className="text-sm text-muted mb-4">Export and share your findings with team members and stakeholders.</p>
            </div>
            <div>
              <h4 className="font-medium text-secondary mb-2">4. Monitor Trends</h4>
              <p className="text-sm text-muted mb-4">Track performance trends and get actionable recommendations.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};