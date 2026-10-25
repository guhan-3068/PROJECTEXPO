import React, { Component } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ApplicationViewPage from './pages/ApplicationViewPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import PreCheckWizardPage from './pages/PreCheckWizardPage';
import OfficialServicesPage from './pages/OfficialServicesPage';
import CorrectionGuidesPage from './pages/CorrectionGuidesPage';
import FaqHelpPage from './pages/FaqHelpPage';
import RuleChangeRadarPage from './pages/RuleChangeRadarPage';
import DocumentTimelinePage from './pages/DocumentTimelinePage';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('QUBIX UI Error Caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 p-6 text-center">
          <div className="max-w-md w-full bg-white rounded-2xl shadow-lg border border-slate-200 p-8 space-y-4">
            <div className="w-12 h-12 mx-auto rounded-full bg-rose-100 text-rose-600 flex items-center justify-center font-bold text-xl">
              !
            </div>
            <h2 className="text-lg font-bold text-slate-800">Something went wrong</h2>
            <p className="text-xs text-slate-500 leading-relaxed">
              An unexpected error occurred while rendering this view. We have recorded the issue.
            </p>
            {this.state.error?.message && (
              <div className="text-[11px] font-mono text-left bg-slate-100 p-3 rounded-lg text-slate-700 overflow-x-auto">
                {this.state.error.message}
              </div>
            )}
            <div className="pt-2 flex gap-3 justify-center">
              <button
                onClick={() => {
                  this.setState({ hasError: false, error: null });
                  window.location.href = '/dashboard';
                }}
                className="px-4 py-2 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-lg text-xs font-bold transition"
              >
                Go to Dashboard
              </button>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg text-xs font-bold transition"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 text-slate-700">
        <div className="w-10 h-10 border-4 border-[#0f2942]/20 border-t-[#0f2942] rounded-full animate-spin mb-3" />
        <span className="text-xs font-semibold text-slate-600">Verifying security session...</span>
      </div>
    );
  }
  return user ? children : <Navigate to="/login" replace />;
};

const AdminRoute = ({ children }) => {
  const { user, isAdmin, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (!isAdmin) return <Navigate to="/dashboard" replace />;
  return children;
};

const AppContent = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 text-slate-700">
        <img 
          src="/qubix-logo.png" 
          alt="QUBIX Logo" 
          className="w-20 h-20 object-contain mb-4 animate-pulse drop-shadow-sm"
        />
        <h2 className="text-xl font-black text-[#0f2942] tracking-wider">QUBIX</h2>
        <p className="text-xs text-slate-500 mt-1 font-medium">Connecting to document verification services...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />
      <main className="flex-1">
        <ErrorBoundary>
          <Routes>
            <Route
              path="/"
              element={user ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />}
            />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/pre-check"
              element={
                <ProtectedRoute>
                  <PreCheckWizardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/rule-radar"
              element={
                <ProtectedRoute>
                  <RuleChangeRadarPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/document-timeline"
              element={
                <ProtectedRoute>
                  <DocumentTimelinePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/official-services"
              element={<OfficialServicesPage />}
            />
            <Route
              path="/correction-guidance"
              element={<CorrectionGuidesPage />}
            />
            <Route
              path="/help-faq"
              element={<FaqHelpPage />}
            />
            <Route
              path="/applications/:id"
              element={
                <ProtectedRoute>
                  <ApplicationViewPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <AdminRoute>
                  <AdminDashboardPage />
                </AdminRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ErrorBoundary>
      </main>
      <footer className="py-6 border-t border-slate-200 bg-white text-center text-xs text-slate-500">
        <div className="flex items-center justify-center space-x-2 mb-1.5">
          <img src="/qubix-logo.png" alt="QUBIX" className="h-5 w-5 object-contain" />
          <span className="font-black text-[#0f2942] tracking-wider">QUBIX</span>
          <span className="text-slate-300">|</span>
          <span className="text-slate-500 font-medium">Smart Document Verification System</span>
        </div>
        <p className="text-[11px] text-slate-400">
          &copy; 2026 QUBIX – Indian Citizen Document Readiness & Verification System. All rights reserved.
        </p>
      </footer>
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
};

export default App;
