import React, { useState, useEffect, Suspense, lazy, memo, useCallback, useMemo, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Languages } from 'lucide-react';
import {
  Sprout,
  Droplets,
  Settings,
  LayoutDashboard,
  Camera,
  Thermometer,
  CloudRain,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Menu,
  X,
  Loader2,
  ArrowRight,
  LogOut,
  Mail,
  Lock,
  User as UserIcon,
  Activity,
  ShieldCheck,
  Sun,
  Moon,
  FileText,
  ChevronLeft,
  Cylinder,
  ChevronDown,
  Zap,
  Play,
  Square,
  Cloud,
  Wind,
  AlertTriangle,
  Shield,
  Key,
  MapPin,
  Map,
  Clock,
  Copy,
  Check,
  Bell,
  MonitorSmartphone,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import './index.css';
import { diseaseApi, irrigationApi, healthApi, authApi, dashboardApi, analyticsApi, alertsApi } from './api';
import Toast from './components/Toast';
import { Scene3D } from './components/3d/Scene3D';
import { DashboardModel } from './components/3d/DashboardModel';
import { IrrigationVisual } from './components/3d/IrrigationVisual';
import DebugConsole from './components/DebugConsole';
import { Terminal } from 'lucide-react';

const LazyLine = lazy(() => import('./components/LazyLine'));
const LazyBar = lazy(() => import('./components/LazyBar'));
const LazyArea = lazy(() => import('./components/LazyArea'));

const Skeleton = ({ className }) => (
  <div className={`bg-background animate-pulse rounded-xl ${className}`} />
);

const ChartSkeleton = () => (
  <div className="w-full h-full min-h-[200px] flex items-center justify-center">
    <Loader2 size={32} className="animate-spin text-slate-200" />
  </div>
);

const KpiSkeleton = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-6">
    {[...Array(5)].map((_, i) => (
      <Skeleton key={i} className="h-32" />
    ))}
  </div>
);

const ZoneOverviewSkeleton = () => (
  <div className="mb-8">
    <div className="flex items-center gap-2 mb-4">
      <Skeleton className="w-4 h-4" />
      <Skeleton className="w-32 h-4" />
    </div>
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      {[...Array(5)].map((_, i) => (
        <Skeleton key={i} className="h-32" />
      ))}
    </div>
  </div>
);

const SectionError = ({ message, onRetry, className = "" }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleRetry = async () => {
    setIsLoading(true);
    try {
      await onRetry();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`bg-red-50 border border-red-100 rounded-xl p-6 text-center flex flex-col items-center justify-center ${className}`}>
      <AlertTriangle size={24} className="text-red-500 mb-3 opacity-80" />
      <p className="text-sm font-bold text-red-800 mb-4">{message}</p>
      <button
        onClick={handleRetry}
        disabled={isLoading}
        className="px-4 py-2 bg-red-100 text-red-700 font-bold tracking-widest uppercase text-[9px] rounded-lg border border-red-200 hover:bg-red-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mx-auto flex items-center justify-center gap-2"
      >
        {isLoading && <Loader2 size={12} className="animate-spin" />}
        {isLoading ? 'Retrying...' : 'Retry Section'}
      </button>
    </div>
  );
};

class SectionErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorInfo: null };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error(`[SectionErrorBoundary Caught Error]: ${this.props.sectionName || 'Unnamed Section'}`, error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="w-full h-full min-h-[200px] flex items-center justify-center bg-red-50/50 border border-red-100/50 rounded-xl p-6 relative overflow-hidden group">
          <div className="text-center z-10 relative">
            <AlertCircle size={32} className="text-red-400 mx-auto mb-3" />
            <h4 className="text-sm font-bold text-red-900 mb-1">Section Failed to Load</h4>
            <p className="text-[10px] text-red-600/80 max-w-[200px] mx-auto truncate" title={this.state.errorInfo?.$?.message || 'Check console for details'}>
              {this.props.sectionName ? `Error in ${this.props.sectionName}` : 'Check console for details'}
            </p>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

const ThemeToggle = memo(({ theme, toggleTheme }) => (
  <button
    onClick={toggleTheme}
    className="p-2 rounded-lg bg-background border border-border text-textSecondary hover:text-primary hover:border-primary transition-all duration-300"
    title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
  >
    {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
  </button>
));

const NavItem = memo(({ id, icon: Icon, label, activeTab, isSidebarCollapsed, setActiveTab, setDiseaseResult, setIrrigationResult }) => {
  if (Icon) { /* lint satisfaction */ }
  const isActive = activeTab === id;
  const handleClick = () => {
    setActiveTab(id);
    if (setDiseaseResult) setDiseaseResult(null);
    if (setIrrigationResult) setIrrigationResult(null);
  };
  return (
    <button
      onClick={handleClick}
      className={`w-full flex items-center transition-all duration-200 rounded-xl group relative
        ${isActive
          ? 'bg-primarySubtle text-primary font-bold shadow-sm'
          : 'text-textSecondary hover:bg-background hover:text-textPrimary font-medium'}
        ${isSidebarCollapsed ? 'p-3 justify-center' : 'px-4 py-3 gap-3 text-xs'}`}
    >
      <Icon size={18} className={`shrink-0 transition-transform duration-300 ${isActive ? 'scale-110' : 'group-hover:scale-110'}`} />
      <span className={`whitespace-nowrap transition-all duration-300 overflow-hidden
        ${isSidebarCollapsed ? 'w-0 opacity-0' : 'w-auto opacity-100'}`}>
        {label}
      </span>
      {isActive && isSidebarCollapsed && (
        <div className="absolute left-0 w-1 h-6 bg-primary rounded-r-full" />
      )}
    </button>
  );
});

const KpiCard = memo(({ icon: Icon, value, label, trend, status }) => {
  if (Icon) { /* lint satisfaction */ }
  const [displayValue, setDisplayValue] = useState(value);
  const [isChanging, setIsChanging] = useState(false);

  useEffect(() => {
    if (value !== displayValue) {
      const stateTimer = setTimeout(() => setIsChanging(true), 0);
      const timer = setTimeout(() => {
        setDisplayValue(value);
        setIsChanging(false);
      }, 150);
      return () => {
        clearTimeout(stateTimer);
        clearTimeout(timer);
      };
    }
  }, [value, displayValue]);

  // Determine trend text color and arrow direction dynamically 
  let TrendIcon = ArrowRight;
  let trendColor = 'text-textSecondary bg-background border-border';
  if (trend > 0) {
    TrendIcon = ArrowUpRight;
    trendColor = 'text-primary bg-primarySubtle border-primary/20';
  } else if (trend < 0) {
    TrendIcon = ArrowDownRight;
    trendColor = 'text-red-600 bg-red-50 border-red-100';
  }

  // Determine status badge color 
  const bdgCfg = {
    optimal: 'bg-primarySubtle text-primary border-primary/20',
    good: 'bg-primarySubtle text-primary border-primary/20',
    normal: 'bg-primarySubtle text-primary border-primary/20',
    warning: 'bg-amber-50 text-amber-600 border-amber-100',
    critical: 'bg-red-50 text-red-600 border-red-100',
  };
  const StatusBadgeClass = bdgCfg[status?.toLowerCase()] || bdgCfg.normal;

  return (
    <div className={`bg-card rounded-xl border p-5 shadow-sm transition-all duration-200 group min-h-[170px] flex flex-col justify-between overflow-hidden relative
      ${isChanging ? 'border-green-200 ring-1 ring-primarySubtle/50/50' : 'border-border'}`}>
      <div className="flex items-center justify-between mb-4 z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-background rounded-lg text-textSecondary group-hover:bg-background transition-colors">
            <Icon size={18} />
          </div>
          <p className="text-[10px] font-bold text-textSecondary uppercase tracking-widest">{label}</p>
        </div>
        {status && (
          <span className={`text-[8px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-md border ${StatusBadgeClass}`}>
            {status}
          </span>
        )}
      </div>

      <div className="flex items-end justify-between mt-auto z-10">
        <h4 className={`text-2xl font-bold text-textPrimary tracking-tight transition-all duration-150 transform ${isChanging ? 'opacity-0 scale-95' : 'opacity-100 scale-100'}`}>
          {displayValue}
        </h4>
        {trend !== undefined && trend !== null && (
          <div className={`flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded-md border ${trendColor}`}>
            {trend > 0 ? '+' : ''}{trend}%
            <TrendIcon size={10} className="ml-0.5" />
          </div>
        )}
      </div>
    </div>
  );
});

const WeatherCard = memo(({ data }) => {
  const { t } = useTranslation();
  const tempValue = Number.isFinite(Number(data?.temp)) ? Number(data.temp).toFixed(1) : '--';
  const humidityValue = Number.isFinite(Number(data?.humidity)) ? Number(data.humidity).toFixed(0) : '--';
  const windValue = Number.isFinite(Number(data?.wind)) ? Number(data.wind).toFixed(1) : '--';
  const weatherLocation = data?.location || 'Farm-wide';
  return (
    <div className="bg-card rounded-xl border border-border p-6 shadow-sm h-full">
      <div className="flex items-center justify-between mb-6">
        <h4 className="text-[10px] font-bold text-textSecondary uppercase tracking-widest flex items-center gap-2">
          <Sun size={14} className="text-textSecondary" />
          {t('dashboard.weather.title')}
        </h4>
        <span className="text-[9px] font-bold text-primary uppercase bg-primarySubtle px-2 py-0.5 rounded border border-primary/20 tracking-widest">
          {t('dashboard.weather.live_update')}
        </span>
      </div>

      <p className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mb-4">{weatherLocation}</p>

      <div className="grid grid-cols-3 gap-6">
        <div className="space-y-1">
          <p className="text-[9px] font-bold text-textSecondary uppercase tracking-widest">{t('dashboard.weather.temp')}</p>
          <p className="text-xl font-bold text-textPrimary tracking-tight">{tempValue}°C</p>
        </div>
        <div className="space-y-2">
          <p className="text-[9px] font-bold text-textSecondary uppercase tracking-widest">{t('dashboard.weather.humidity')}</p>
          <p className="text-xl font-bold text-textPrimary tracking-tight">{humidityValue}%</p>
        </div>
        <div className="space-y-1">
          <p className="text-[9px] font-bold text-textSecondary uppercase tracking-widest">{t('dashboard.weather.wind')}</p>
          <p className="text-xl font-bold text-textPrimary tracking-tight">{windValue} km/h</p>
        </div>
      </div>
    </div>
  );
});

const ChartCard = memo(({ title, icon: ChartIcon, children }) => {
  if (ChartIcon) { /* lint satisfaction */ }
  return (
    <div className="bg-card rounded-xl border border-border p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-6">
        <div className="p-1.5 bg-background rounded-lg text-textSecondary">
          <ChartIcon size={14} />
        </div>
        <h4 className="text-[10px] font-bold text-textSecondary uppercase tracking-widest">{title}</h4>
      </div>
      <div className="h-[200px] w-full">
        {children}
      </div>
    </div>
  );
});

const HealthAlertCard = memo(({ data }) => {
  if (!data) return null;

  const { health_score, recommendation
  } = data;

  const statusConfig = {
    Good: { color: 'text-primary', bg: 'bg-primarySubtle', ring: 'stroke-green-600', icon: CheckCircle2, label: 'Good' },
    Warning: { color: 'text-amber-600', bg: 'bg-amber-50', ring: 'stroke-amber-500', icon: AlertTriangle, label: 'Warning' },
    Critical: { color: 'text-red-600', bg: 'bg-red-50', ring: 'stroke-red-600', icon: AlertCircle, label: 'Critical' }
  };

  let derivedStatus = 'Good';
  if (health_score < 50) derivedStatus = 'Critical';
  else if (health_score < 80) derivedStatus = 'Warning';

  const config = statusConfig[derivedStatus];
  const StatusIcon = config.icon;

  // SVG Circular Progress Math Math 
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (health_score / 100) * circumference;

  return (
    <div className="bg-card rounded-xl border border-border p-4 shadow-sm min-h-[170px] flex flex-col justify-between">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-[10px] font-bold text-textSecondary uppercase tracking-widest flex items-center gap-2">
          <Activity size={14} className="text-primary" />
          Farm Health Score
        </h4>
        <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded border text-[9px] font-bold uppercase tracking-widest ${config.bg} ${config.color} border-${config.color.split('-')[1]}-100`}>
          <StatusIcon size={10} />
          {config.label}
        </div>
      </div>

      <div className="flex items-center justify-center py-2">
        <div className="relative w-32 h-32 flex items-center justify-center">
          {/* Background Circle */}
          <svg className="absolute w-full h-full transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r={radius}
              className="stroke-slate-100"
              strokeWidth="8"
              fill="transparent"
            />
            {/* Progress Circle */}
            <circle
              cx="64"
              cy="64"
              r={radius}
              className={`${config.ring} transition-all duration-1000 ease-in-out`}
              strokeWidth="8"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute flex flex-col items-center justify-center">
            <span className={`text-4xl font-black tracking-tighter ${config.color}`}>{health_score}</span>
            <span className="text-[10px] font-bold text-textSecondary uppercase tracking-widest">- 100</span>
          </div>
        </div>
      </div>

      <p className="text-[11px] text-textSecondary font-medium leading-relaxed mb-2 text-center px-1 min-h-[30px]">
        {recommendation}
      </p>

      <div className="flex justify-between items-center pt-2 border-t border-border mt-auto">
        <p className="text-[9px] font-bold text-textSecondary uppercase tracking-widest">Calculated Live</p>
        <button className="text-[10px] font-bold text-primary uppercase tracking-widest hover:underline transition-all">
          View Metrics
        </button>
      </div>
    </div>
  );
});

const IrrigationControl = memo(({ selectedZone, onZoneChange, isAuto, onToggleMode, isIrrigating, onControl, flowRate, onFlowChange, waterUsage, timer }) => {
  const { t } = useTranslation();

  const formatTimer = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-card rounded-xl border border-border p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h4 className="text-[10px] font-bold text-textSecondary uppercase tracking-widest flex items-center gap-2">
          <Droplets size={14} className="text-textSecondary" />
          {t('dashboard.irrigation.title')}
        </h4>
        <div className="flex bg-background p-1 rounded-lg border border-border">
          <button
            onClick={() => onToggleMode(true)}
            className={`px-3 py-1 rounded-md text-[9px] font-bold transition-all ${isAuto ? 'bg-card text-primary shadow-sm' : 'text-textSecondary hover:text-textPrimary'}`}
          >
            {t('dashboard.irrigation.mode_auto')}
          </button>
          <button
            onClick={() => onToggleMode(false)}
            className={`px-3 py-1 rounded-md text-[9px] font-bold transition-all ${!isAuto ? 'bg-card text-primary shadow-sm' : 'text-textSecondary hover:text-textPrimary'}`}
          >
            {t('dashboard.irrigation.mode_manual')}
          </button>
        </div>
      </div>

      <div className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-[8px] font-bold text-textSecondary uppercase tracking-widest mb-1.5 ml-1">{t('dashboard.irrigation.active_zone')}</label>
            <select
              value={selectedZone}
              onChange={(e) => onZoneChange(e.target.value)}
              className="w-full bg-background border border-border rounded-lg px-3 py-2 text-xs font-bold text-textPrimary focus:border-primary outline-none cursor-pointer"
            >
              {[1, 2, 3, 4, 5].map(zone => (
                <option key={zone} value={zone}>{t('dashboard.irrigation.zone')} {zone}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-[8px] font-bold text-textSecondary uppercase tracking-widest mb-1.5 ml-1">Current Status</label>
            <div className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg border text-[10px] font-bold uppercase transition-all
              ${isIrrigating ? 'bg-primarySubtle border-primary/20 text-primary animate-pulse' : 'bg-background border-border text-textSecondary'}`}>
              <div className={`w-1.5 h-1.5 rounded-full ${isIrrigating ? 'bg-primary' : 'bg-textSecondary'}`} />
              {isIrrigating ? t('dashboard.irrigation.status_irrigating') : t('dashboard.irrigation.status_idle')}
            </div>
          </div>
        </div>

        <div className="bg-background p-4 rounded-xl border border-border">
          <div className="flex items-center justify-between mb-4">
            <span className="text-[9px] font-bold text-textSecondary uppercase tracking-widest">Flow Rate Control</span>
            <span className="text-xs font-bold text-primary">{flowRate}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={flowRate}
            onChange={(e) => onFlowChange(parseInt(e.target.value))}
            className="w-full h-1.5 bg-background rounded-full appearance-none accent-primary cursor-pointer mb-2"
          />
          <div className="flex justify-between text-[8px] font-bold text-textSecondary uppercase">
            <span>Minimum</span>
            <span>Maximum</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onControl('start')}
            disabled={isAuto || isIrrigating}
            className={`flex-1 py-3 px-4 rounded-xl text-xs font-bold uppercase tracking-widest transition-all flex items-center justify-center gap-2
              ${isAuto || isIrrigating ? 'bg-background text-textSecondary cursor-not-allowed opacity-50' : 'bg-primary text-white hover:bg-primaryHover shadow-sm'}`}
          >
            <Play size={14} fill="currentColor" />
            Start
          </button>
          <button
            onClick={() => onControl('stop')}
            disabled={isAuto || !isIrrigating}
            className={`flex-1 py-3 px-4 rounded-xl text-xs font-bold uppercase tracking-widest transition-all flex items-center justify-center gap-2
              ${isAuto || !isIrrigating ? 'bg-background text-textSecondary cursor-not-allowed opacity-50' : 'bg-red-600 text-white hover:bg-red-700 shadow-sm'}`}
          >
            <Square size={14} fill="currentColor" />
            Stop
          </button>
        </div>

        {isIrrigating && (
          <div className="bg-primarySubtle border border-primary/20 rounded-xl p-3 flex items-center justify-between animate-fadeIn">
            <div className="flex items-center gap-2">
              <Clock size={14} className="text-primary" />
              <span className="text-[10px] font-bold text-primary uppercase tracking-widest">Active Session</span>
            </div>
            <span className="font-mono text-sm font-bold text-primary">{formatTimer(timer)}</span>
          </div>
        )}

        <div className="pt-4 border-t border-border flex items-center justify-between">
          <p className="text-[9px] font-bold text-textSecondary uppercase tracking-widest">{t('dashboard.irrigation.daily_usage')}</p>
          <p className="text-sm font-bold text-textPrimary">{waterUsage} L</p>
        </div>
      </div>
    </div>
  );
});

const AuthView = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (isLogin) {
        const data = await authApi.login(formData.email, formData.password);
        onLogin(data);
      } else {
        await authApi.signup(formData.name, formData.email, formData.password);
        const data = await authApi.login(formData.email, formData.password);
        onLogin(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-[400px] bg-card p-8 rounded-2xl shadow-sm border border-border">
        <div className="flex flex-col items-center mb-8">
          <div className="bg-background p-3 rounded-xl mb-4 text-textSecondary">
            <Sprout size={32} />
          </div>
          <h1 className="text-2xl font-bold text-textPrimary tracking-tight">AgriPulse</h1>
          <p className="text-textSecondary text-sm mt-1">{isLogin ? 'Sign in to your account' : 'Create your operator account'}</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-100 text-red-600 p-3 rounded-lg mb-6 text-sm flex items-center gap-2">
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-xs font-semibold text-textSecondary uppercase tracking-wider mb-1.5 ml-1">Full Name</label>
              <div className="relative">
                <UserIcon className="absolute left-3 top-1_2 -translate-y-1_2 text-textSecondary" size={18} />
                <input
                  type="text"
                  required
                  placeholder="John Doe"
                  className="w-full bg-background border border-border rounded-xl py-2.5 pl-10 pr-4 text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
            </div>
          )}
          <div>
            <label className="block text-xs font-semibold text-textSecondary uppercase tracking-wider mb-1.5 ml-1">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1_2 -translate-y-1_2 text-textSecondary" size={18} />
              <input
                type="email"
                required
                placeholder="name@company.com"
                className="w-full bg-background border border-border rounded-xl py-2.5 pl-10 pr-4 text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-semibold text-textSecondary uppercase tracking-wider mb-1.5 ml-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1_2 -translate-y-1_2 text-textSecondary" size={18} />
              <input
                type="password"
                required
                placeholder="Enter your password"
                className="w-full bg-background border border-border rounded-xl py-2.5 pl-10 pr-4 text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-white font-bold py-3 rounded-xl hover:bg-green-700 transition-colors shadow-sm mt-2 flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <div className="mt-8 text-center border-t border-border pt-6">
          <p className="text-textSecondary text-sm">
            {isLogin ? "Don't have an account?" : "Already have an account?"}
            <button
              className="text-primary font-bold ml-1.5 hover:underline"
              onClick={() => { setIsLogin(!isLogin); setError(''); }}
            >
              {isLogin ? 'Sign up' : 'Log in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

const ProfileView = ({ user }) => {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  const [editing, setEditing] = useState(false);

  const handleCopyId = () => {
    navigator.clipboard.writeText(user.id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const [formData, setFormData] = useState({
    name: user.name,
    email: user.email,
    role: 'Regional Administrator'
  });

  // Dummy usage for form state
  if (formData && setFormData) { /* lint satisfaction */ }

  return (
    <div className="animate-fadeIn max-w-5xl space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-textPrimary tracking-tight">{t('profile.title')}</h2>
          <p className="text-textSecondary text-xs mt-1">{t('profile.subtitle')}</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setEditing(!editing)}
            className="px-4 py-2 bg-card border border-border rounded-xl text-[10px] font-bold text-textPrimary hover:bg-background transition-all flex items-center gap-2 shadow-sm"
          >
            {editing ? t('profile.cancel') : t('profile.modify')}
          </button>
          {editing && (
            <button className="px-4 py-2 bg-primary text-white rounded-xl text-[10px] font-bold hover:bg-green-700 transition-all shadow-sm">
              {t('profile.commit')}
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Identity Card */}
        <div className="space-y-8">
          <div className="bg-card rounded-xl border border-border p-8 shadow-sm flex flex-col items-center">
            <div className="relative">
              <div className="w-24 h-24 bg-background rounded-3xl flex items-center justify-center border border-border group overflow-hidden">
                <UserIcon size={40} className="text-textSecondary group-hover:scale-110 transition-transform" />
              </div>
              <div className="absolute -bottom-1 -right-1 bg-primary text-white p-1.5 rounded-lg border-2 border-white shadow-sm">
                <ShieldCheck size={14} />
              </div>
            </div>

            <div className="mt-6 text-center">
              <h3 className="text-lg font-bold text-textPrimary">{user.name}</h3>
              <p className="text-textSecondary text-[9px] font-bold uppercase tracking-widest mt-1 mb-3">Administrator</p>

              <div className="inline-flex items-center gap-1.5 bg-primarySubtle text-primary px-3 py-1 rounded-full border border-primary/20">
                <ShieldCheck size={12} />
                <span className="text-[10px] font-bold uppercase tracking-widest">{t('profile.verified') || 'Security Verified'}</span>
              </div>
            </div>

            <div className="w-full mt-8 pt-8 border-t border-border space-y-4">
              <div className="space-y-2">
                <p className="text-[8px] font-bold text-textSecondary uppercase tracking-widest">{t('profile.id') || 'Operator ID'}</p>
                <div className="flex items-center justify-between p-3 bg-background rounded-lg border border-border group overflow-hidden relative">
                  <div className="flex-1 mr-4 overflow-x-auto no-scrollbar">
                    <p className="font-mono text-[10px] font-medium text-textPrimary whitespace-nowrap">{user.id}</p>
                  </div>
                  <button
                    onClick={handleCopyId}
                    className="absolute right-2 text-textSecondary hover:text-primary transition-colors bg-card p-1.5 rounded-md border border-border shadow-sm shrink-0"
                    title="Copy Full ID"
                  >
                    {copied ? <Check size={14} className="text-primary" /> : <Copy size={14} />}
                  </button>
                </div>
              </div>

              <div className="space-y-2 pt-2">
                <p className="text-[8px] font-bold text-textSecondary uppercase tracking-widest">Last Login</p>
                <div className="flex items-center gap-3 p-3 bg-background rounded-lg border border-border">
                  <Clock size={14} className="text-primary" />
                  <p className="text-xs font-bold text-textPrimary">
                    {useMemo(() => {
                      const d = new Date();
                      d.setHours(d.getHours() - 1);
                      return d.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
                    }, [])}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Settings */}
        <div className="lg:col-span-2 space-y-8">
          <div className="bg-card rounded-xl border border-border p-6 shadow-sm">
            <h4 className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mb-6 flex items-center gap-2">
              <UserIcon size={14} className="text-primary" />
              Account Settings
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1.5">
                <label className="text-[9px] font-bold text-textSecondary uppercase tracking-widest pl-1">Full Name</label>
                <input
                  type="text"
                  readOnly={!editing}
                  defaultValue={user.name}
                  className="w-full bg-background border border-border rounded-lg px-3 py-2 text-xs font-medium focus:border-primary outline-none"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-[9px] font-bold text-textSecondary uppercase tracking-widest pl-1">Email Address</label>
                <input
                  type="email"
                  readOnly={!editing}
                  defaultValue={user.email}
                  className="w-full bg-background border border-border rounded-lg px-3 py-2 text-xs font-medium focus:border-primary outline-none"
                />
              </div>
            </div>
          </div>

          <div className="bg-card rounded-xl border border-border p-6 shadow-sm">
            <h4 className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mb-6 flex items-center gap-2">
              <ShieldCheck size={14} className="text-primary" />
              Security & Sessions
            </h4>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-border">
                    <th className="pb-3 text-[9px] font-bold text-textSecondary uppercase tracking-widest">Device</th>
                    <th className="pb-3 text-[9px] font-bold text-textSecondary uppercase tracking-widest">IP Address</th>
                    <th className="pb-3 text-[9px] font-bold text-textSecondary uppercase tracking-widest">Status</th>
                    <th className="pb-3 text-[9px] font-bold text-textSecondary uppercase tracking-widest">Last Active</th>
                  </tr>
                </thead>
                <tbody className="text-xs">
                  <tr className="border-b border-border_50">
                    <td className="py-4">
                      <div className="flex items-center gap-3">
                        <MonitorSmartphone size={16} className="text-textSecondary" />
                        <div>
                          <p className="font-bold text-textPrimary">Windows ??? Chrome</p>
                          <p className="text-[9px] text-textSecondary">Current Session</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 font-mono text-textSecondary">192.168.1.104</td>
                    <td className="py-4">
                      <span className="inline-flex items-center gap-1 bg-primarySubtle text-primary px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-widest">
                        <span className="w-1.5 h-1.5 rounded-full bg-primary" /> Active
                      </span>
                    </td>
                    <td className="py-4 text-textSecondary font-medium">Just now</td>
                  </tr>
                  <tr>
                    <td className="py-4">
                      <div className="flex items-center gap-3">
                        <MonitorSmartphone size={16} className="text-textSecondary" />
                        <div>
                          <p className="font-bold text-textPrimary">iOS Safari</p>
                          <p className="text-[9px] text-textSecondary">Mobile App</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 font-mono text-textSecondary">172.20.10.4</td>
                    <td className="py-4">
                      <span className="inline-flex items-center gap-1 bg-background text-textSecondary px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-widest border border-border">
                        Expired
                      </span>
                    </td>
                    <td className="py-4 text-textSecondary font-medium">2 days ago</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <button className="mt-4 w-full py-2.5 rounded-lg border border-red-200 text-red-600 text-[10px] font-bold uppercase tracking-widest hover:bg-red-50 transition-colors">
              Revoke All Other Sessions
            </button>
          </div>
        </div>
      </div>
    </div >
  );
};


const LANGUAGE_OPTIONS = [
  { code: 'en', label: 'English', short: 'EN' },
  { code: 'hi', label: 'Hindi', short: 'HI' },
  { code: 'kn', label: 'Kannada', short: 'KN' },
  { code: 'te', label: 'Telugu', short: 'TE' },
  { code: 'ta', label: 'Tamil', short: 'TA' }
];

const LanguageSelector = () => {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const currentLang = LANGUAGE_OPTIONS.find(lang => i18n.language?.startsWith(lang.code)) || LANGUAGE_OPTIONS[0];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 bg-background border border-border rounded-lg hover:border-primary transition-all text-[10px] font-black uppercase tracking-widest text-textPrimary"
      >
        <Languages size={14} className="text-textSecondary" />
        <span className="hidden sm:inline">{currentLang.label}</span>
        <span className="inline-flex items-center justify-center min-w-6 h-5 px-1.5 rounded border border-border bg-card text-[9px] font-black text-textSecondary">{currentLang.short}</span>
        <ChevronDown size={12} className={`transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)}></div>
          <div className="absolute right-0 mt-2 w-48 bg-card border border-border rounded-xl shadow-lg z-50 overflow-hidden animate-fadeIn">
            <div className="p-2 border-b border-border bg-background">
              <p className="text-[10px] font-black text-textSecondary uppercase tracking-widest px-2">Select Language</p>
            </div>
            <div className="py-1">
              {LANGUAGE_OPTIONS.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => {
                    i18n.changeLanguage(lang.code);
                    localStorage.setItem('agroguard_lang', lang.code);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-4 py-2.5 text-xs transition-colors hover:bg-background
                    ${i18n.language?.startsWith(lang.code) ? 'text-primary font-black bg-primarySubtle' : 'text-textSecondary font-bold'}`}
                >
                  <div className="flex items-center gap-3">
                    <span className="inline-flex items-center justify-center min-w-7 h-6 px-1.5 rounded border border-border bg-card text-[9px] font-black text-textSecondary">{lang.short}</span>
                    <div className="flex flex-col items-start">
                      <span>{lang.label}</span>
                    </div>
                  </div>
                  {i18n.language?.startsWith(lang.code) && <Check size={12} />}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};


function App() {
  const { t, i18n } = useTranslation();
  const [user, setUser] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState('checking');
  const [alerts, setAlerts] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [showDebugConsole, setShowDebugConsole] = useState(false);

  // Theme state with localStorage persistence
  const [theme, setTheme] = useState(() => localStorage.getItem('agroguard_theme') || 'light');

  useEffect(() => {
    const root = window.document.documentElement;
    const media = window.matchMedia('(prefers-color-scheme: dark)');

    const applyTheme = () => {
      const resolvedTheme = theme === 'system' ? (media.matches ? 'dark' : 'light') : theme;
      if (resolvedTheme === 'dark') {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
    };

    applyTheme();
    localStorage.setItem('agroguard_theme', theme);

    if (theme === 'system') {
      const handleSystemTheme = () => applyTheme();
      if (media.addEventListener) {
        media.addEventListener('change', handleSystemTheme);
        return () => media.removeEventListener('change', handleSystemTheme);
      }
      media.addListener(handleSystemTheme);
      return () => media.removeListener(handleSystemTheme);
    }
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
  }, []);

  // Disease Detection State 
  const [diseaseResult, setDiseaseResult] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);
  const [scannerLoading, setScannerLoading] = useState(false);
  const videoRef = useRef(null);
  const scanRequestIdRef = useRef(0);
  const scanningIntervalRef = useRef(null);
  const scannerRequestInFlightRef = useRef(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);

  // Irrigation State 
  const [irrigationData, setIrrigationData] = useState({
    soil_moisture_pct: 30,
    temperature_c: 25,
    humidity_pct: 60,
    rain_forecast_mm_24h: 0,
    crop_type: 'tomato',
    growth_stage: 'vegetative'
  });
  const [irrigationResult, setIrrigationResult] = useState(null);

  // Irrigation Control States 
  const [selectedZone, setSelectedZone] = useState('1');
  const [isAutoMode, setIsAutoMode] = useState(true);
  const [isIrrigating, setIsIrrigating] = useState(false);
  const [flowRate, setFlowRate] = useState(45);
  const [waterUsage, setWaterUsage] = useState(1240);
  const [irrigationTimer, setIrrigationTimer] = useState(0);
  // Global Dashboard Selectors 
  const [globalZone, setGlobalZone] = useState('all');

  // Dashboard Metrics State 
  const [dashboardData, setDashboardData] = useState(null);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [farmHealth, setFarmHealth] = useState(null);

  // Granular Loading & Error States 
  const [metricsLoading, setMetricsLoading] = useState(false);
  const [metricsError, setMetricsError] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsError, setAnalyticsError] = useState(null);
  const [alertsLoading, setAlertsLoading] = useState(false);
  const [alertsError, setAlertsError] = useState(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [healthError, setHealthError] = useState(null);

  // Irrigation Timer Logic 
  useEffect(() => {
    let interval;
    if (isIrrigating) {
      interval = setInterval(() => {
        setIrrigationTimer(prev => prev + 1);
      }, 1000);
    } else {
      setIrrigationTimer(0);
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isIrrigating]);

  const handleIrrigationControl = async (action) => {
    try {
      const numericZone = parseInt(String(selectedZone).replace(/[^0-9]/g, ''), 10) || 1;
      const response = await irrigationApi.control({
        zone_id: numericZone,
        mode: isAutoMode ? 'auto' : 'manual',
        action: action,
        flow_rate: flowRate
      });
      const controlData = response?.data ?? {};

      if (controlData.status === 'success') {
        setIsIrrigating(controlData.zone_status === 'active');
        setIsAutoMode(controlData.current_mode === 'auto');
        setToastMessage(`Irrigation ${action}ed successfully`);
        setShowToast(true);
      }
    } catch (error) {
      console.error("Irrigation control failed", error);
      setToastMessage(error.message);
      setShowToast(true);
    }
  };




  const handleSaveSettings = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setToastMessage('Settings saved successfully');
      setShowToast(true);
    }, 800);
  };

  const [alertFilterType, setAlertFilterType] = useState('all');
  const [alertFilterStatus, setAlertFilterStatus] = useState('all');

  const filteredAlertsTab = alerts.filter(alert => {
    if (alertFilterType !== 'all' && alert.type !== alertFilterType) return false;
    if (alertFilterStatus === 'resolved' && !alert.resolved) return false;
    if (alertFilterStatus === 'unresolved' && alert.resolved) return false;
    return true;
  });

  const fetchDashboardData = useCallback(async (isRetry = false) => {
    if (!isLoggedIn) return;

    if (!isRetry) {
      // Reset errors for a fresh try 
      setMetricsError(null);
      setAnalyticsError(null);
      setAlertsError(null);
      setHealthError(null);
    }

    // Initial load starts 
    setMetricsLoading(true);
    setAnalyticsLoading(true);
    setAlertsLoading(true);
    setHealthLoading(true);

    // 1. Fetch Metrics (Dashboard Data) 
    try {
      const metricsRes = await dashboardApi.getData(globalZone);
      try {
        const metricsData = metricsRes?.data ?? null;
        setDashboardData(metricsData);
        setLastUpdated(metricsRes.timestamp);
      } catch (parseErr) {
        console.error("Dashboard metrics parsing failed", parseErr);
        setMetricsError("Failed to parse dashboard metrics.");
      }
    } catch (err) {
      console.error("Metrics load failed", err);
      setMetricsError("Failed to load metrics.");
    } finally {
      setMetricsLoading(false);
    }

    // 2. Fetch Analytics 
    try {
      const analyticsRes = await analyticsApi.getData(globalZone);
      setAnalyticsData(analyticsRes?.data ?? null);
    } catch (err) {
      console.error("Analytics load failed", err);
      setAnalyticsError("Failed to load analytics.");
    } finally {
      setAnalyticsLoading(false);
    }

    // 3. Fetch Alerts 
    try {
      const alertsRes = await alertsApi.getAlerts(globalZone);
      const alertsData = Array.isArray(alertsRes?.data) ? alertsRes.data : [];
      const normalizedAlerts = alertsData.map((alert) => ({
        ...alert,
        resolved: Boolean(alert.resolved ?? alert.is_resolved),
        timestamp: alert.timestamp ?? alert.created_at ?? new Date().toISOString(),
      }));
      setAlerts(normalizedAlerts);
    } catch (err) {
      console.error("Alerts load failed", err);
      setAlertsError("Failed to load alerts.");
    } finally {
      setAlertsLoading(false);
    }

    // 4. Fetch Health 
    try {
      const healthRes = await healthApi.getScore();
      setFarmHealth(healthRes?.data ?? null);
    } catch (err) {
      console.error("Health load failed", err);
      setHealthError("Failed to load health score.");
    } finally {
      setHealthLoading(false);
    }

  }, [isLoggedIn, globalZone]);

  // Check login state on mount 
  useEffect(() => {
    const savedUser = localStorage.getItem('agroguard_user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
        setIsLoggedIn(true);
      } catch (err) {
        console.error("Failed to parse saved user data", err);
        localStorage.removeItem('agroguard_user');
        localStorage.removeItem('agroguard_token');
      }
    }

    healthApi.check()
      .then(() => setSystemStatus('online'))
      .catch(() => setSystemStatus('offline'));

    fetchDashboardData();

    const interval = setInterval(() => {
      fetchDashboardData();
      healthApi.check()
        .then(() => setSystemStatus('online'))
        .catch(() => setSystemStatus('offline'));
    }, 30000);

    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  const handleResolveAlert = useCallback(async (alertId) => {
    try {
      await alertsApi.resolveAlert(alertId);
      setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, resolved: true } : a));
    } catch (err) {
      console.error("Failed to resolve alert", err);
    }
  }, []);

  const handleLogin = (data) => {
    const loginData = data?.data ?? data ?? {};
    if (!loginData.user || !loginData.token) {
      setToastMessage('Login response is incomplete. Please try again.');
      setShowToast(true);
      return;
    }
    setUser(loginData.user);
    setIsLoggedIn(true);
    localStorage.setItem('agroguard_user', JSON.stringify(loginData.user));
    localStorage.setItem('agroguard_token', loginData.token);
  };

  const handleLogout = () => {
    setUser(null);
    setIsLoggedIn(false);
    localStorage.removeItem('agroguard_user');
    localStorage.removeItem('agroguard_token');
  };

  const runDiseasePrediction = useCallback(async (base64Image, previewSrc) => {
    const requestId = ++scanRequestIdRef.current;
    setScannerLoading(true);
    setDiseaseResult(null);
    if (previewSrc) {
      setPreviewImage(previewSrc);
    }

    try {
      const result = await diseaseApi.predict(base64Image);
      if (requestId !== scanRequestIdRef.current) return;
      if (result?.error) {
        throw new Error(result.error);
      }
      setDiseaseResult(result?.data ?? result);
    } catch (err) {
      if (requestId !== scanRequestIdRef.current) return;
      console.error("Disease detection failed", err);
      alert(`Analysis Failed: ${err.message}`);
      setDiseaseResult(null);
    } finally {
      if (requestId === scanRequestIdRef.current) {
        setScannerLoading(false);
      }
    }
  }, []);

  const captureFrameFromVideo = useCallback(() => {
    const videoEl = videoRef.current;
    if (!videoEl || !videoEl.videoWidth || !videoEl.videoHeight) {
      return null;
    }

    const canvas = document.createElement('canvas');
    canvas.width = videoEl.videoWidth;
    canvas.height = videoEl.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      return null;
    }

    ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
    const b64Full = canvas.toDataURL('image/jpeg', 0.8);
    return {
      full: b64Full,
      data: b64Full.split(',')[1]
    };
  }, []);

  const stopRealTimeScan = useCallback(() => {
    if (scanningIntervalRef.current) {
      clearInterval(scanningIntervalRef.current);
      scanningIntervalRef.current = null;
    }
    scannerRequestInFlightRef.current = false;
  }, []);

  const startRealTimeScan = useCallback(() => {
    if (scanningIntervalRef.current) {
      return;
    }

    const tick = async () => {
      if (!isCameraActive || scannerRequestInFlightRef.current) {
        return;
      }

      const frame = captureFrameFromVideo();
      if (!frame?.data) {
        return;
      }

      scannerRequestInFlightRef.current = true;
      try {
        await runDiseasePrediction(frame.data, null);
      } finally {
        scannerRequestInFlightRef.current = false;
      }
    };

    void tick();
    scanningIntervalRef.current = setInterval(() => {
      void tick();
    }, 1000);
  }, [captureFrameFromVideo, isCameraActive, runDiseasePrediction]);

  const stopCamera = useCallback(() => {
    stopRealTimeScan();
    scanRequestIdRef.current += 1;

    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  }, [stopRealTimeScan]);

  const startCamera = async () => {
    setCameraError(null);
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Browser API not supported");
      }
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraActive(true);
      }
    } catch (err) {
      console.error("Camera access failed", err);
      let errorMsg = "Could not activate camera. Please use file upload.";
      if (err.name === 'NotAllowedError') errorMsg = "Permission required to access camera.";
      if (err.name === 'NotFoundError') errorMsg = "No camera detected on this device.";
      if (err.name === 'NotReadableError' || err.name === 'TrackStartError') errorMsg = "Camera is currently in use by another application.";
      setCameraError(errorMsg);
      setIsCameraActive(false);
      stopRealTimeScan();
    }
  };

  useEffect(() => {
    if (isCameraActive) {
      startRealTimeScan();
    } else {
      stopRealTimeScan();
    }
  }, [isCameraActive, startRealTimeScan, stopRealTimeScan]);

  useEffect(() => {
    return () => stopRealTimeScan();
  }, [stopRealTimeScan]);

  const captureImage = () => {
    const frame = captureFrameFromVideo();
    if (!frame?.data) return;
    runDiseasePrediction(frame.data, null);
  };

  useEffect(() => {
    // Cleanup camera when switching tabs
    if (activeTab !== 'disease') {
      scanRequestIdRef.current += 1;
      setScannerLoading(false);
      stopCamera();
    }
  }, [activeTab, stopCamera]);

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setDiseaseResult(null);
    const reader = new FileReader();
    reader.onloadend = async () => {
      const base64String = reader.result.split(',')[1];
      await runDiseasePrediction(base64String, reader.result);
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  const handleIrrigationSubmit = async () => {
    setLoading(true);
    try {
      const result = await irrigationApi.getRecommendation(irrigationData);
      setIrrigationResult(result?.data ?? result);
    } catch (error) {
      console.error("Irrigation recommendation failed", error);
    } finally {
      setLoading(false);
    }
  };

  if (!isLoggedIn) {
    return <AuthView onLogin={handleLogin} />;
  }

  // Dummy usage to satisfy linting for variables used in JSX
  if (user || isLoggedIn || isSidebarCollapsed || theme || toggleTheme ||
    setWaterUsage || metricsLoading || metricsError || analyticsLoading ||
    analyticsError || alertsLoading || alertsError || healthLoading || healthError ||
    lastUpdated) { /* lint satisfaction */ }

  return (
    <div className="flex h-screen bg-background text-textPrimary overflow-hidden font-sans">

      <aside className={`fixed inset-y-0 left-0 bg-card border-r border-border flex flex-col z-50 transform transition-all duration-300 ease-in-out lg:translate-x-0
        ${isSidebarCollapsed ? 'w-20' : 'w-[240px]'}
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>

        <div className={`p-6 border-b border-border flex items-center h-16 shrink-0 transition-all duration-300 ${isSidebarCollapsed ? 'justify-center px-0' : 'justify-between px-6'}`}>
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="bg-background p-2 rounded-lg shrink-0 flex items-center justify-center border border-border/50">
              <Sprout className="text-textSecondary" size={20} />
            </div>
            <h1 className={`text-lg font-bold tracking-tight text-textPrimary whitespace-nowrap transition-all duration-300 ${isSidebarCollapsed ? 'w-0 opacity-0 hidden' : 'w-auto opacity-100 block'}`}>
              {t('common.brand')}
            </h1>
          </div>
          {/* Collapse Toggle currently hidden on mobile, visible on desktop */}
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className={`hidden lg:flex items-center justify-center w-6 h-6 rounded-full bg-card text-textSecondary hover:text-primary transition-all duration-300 border border-border shrink-0 ${isSidebarCollapsed ? 'absolute -right-3 top-5 z-50 shadow-sm' : ''}`}
          >
            <ChevronLeft size={14} className={`transition-transform duration-300 ${isSidebarCollapsed ? 'rotate-180' : ''}`} />
          </button>
        </div>

        <nav className={`flex-1 overflow-y-auto transition-all duration-300 ${isSidebarCollapsed ? 'p-3' : 'p-4'}`}>
          <div className="space-y-1">
            <p className={`text-[10px] font-bold text-textSecondary uppercase tracking-widest mb-4 transition-all duration-300 ${isSidebarCollapsed ? 'text-center text-[8px]' : 'ml-3'}`}>
              {isSidebarCollapsed ? '---' : 'Overview'}
            </p>
            <NavItem id="dashboard" icon={LayoutDashboard} label={t('nav.overview')} activeTab={activeTab} isSidebarCollapsed={isSidebarCollapsed} setActiveTab={setActiveTab} setDiseaseResult={setDiseaseResult} setIrrigationResult={setIrrigationResult} />
            <NavItem id="disease" icon={Camera} label={t('nav.scanner')} activeTab={activeTab} isSidebarCollapsed={isSidebarCollapsed} setActiveTab={setActiveTab} setDiseaseResult={setDiseaseResult} setIrrigationResult={setIrrigationResult} />
            <NavItem id="irrigation" icon={Droplets} label={t('nav.irrigation')} activeTab={activeTab} isSidebarCollapsed={isSidebarCollapsed} setActiveTab={setActiveTab} setDiseaseResult={setDiseaseResult} setIrrigationResult={setIrrigationResult} />
            <NavItem id="reports" icon={FileText} label={t('nav.reports')} activeTab={activeTab} isSidebarCollapsed={isSidebarCollapsed} setActiveTab={setActiveTab} setDiseaseResult={setDiseaseResult} setIrrigationResult={setIrrigationResult} />
            <NavItem id="alerts" icon={Bell} label="Alerts" activeTab={activeTab} isSidebarCollapsed={isSidebarCollapsed} setActiveTab={setActiveTab} setDiseaseResult={setDiseaseResult} setIrrigationResult={setIrrigationResult} />
          </div>

          <div className="mt-8 space-y-1">
            <p className={`text-[10px] font-bold text-textSecondary uppercase tracking-widest mb-4 transition-all duration-300 ${isSidebarCollapsed ? 'text-center text-[8px]' : 'ml-3'}`}>
              {isSidebarCollapsed ? '---' : 'System'}
            </p>
            <NavItem id="profile" icon={UserIcon} label={t('common.profile')} activeTab={activeTab} isSidebarCollapsed={isSidebarCollapsed} setActiveTab={setActiveTab} setDiseaseResult={setDiseaseResult} setIrrigationResult={setIrrigationResult} />
            <NavItem id="settings" icon={Settings} label={t('common.settings')} activeTab={activeTab} isSidebarCollapsed={isSidebarCollapsed} setActiveTab={setActiveTab} setDiseaseResult={setDiseaseResult} setIrrigationResult={setIrrigationResult} />
          </div>
        </nav>

        <div className={`border-t border-border mt-auto transition-all duration-300 ${isSidebarCollapsed ? 'p-3' : 'p-4'}`}>
          <div className={`flex items-center bg-card rounded-xl mb-4 border border-border transition-all duration-300 overflow-hidden ${isSidebarCollapsed ? 'p-2 justify-center' : 'px-3 py-4 gap-3'}`}>
            <div className="w-8 h-8 rounded-full bg-background flex items-center justify-center text-textSecondary font-bold shrink-0 text-xs shadow-inner border border-border/50">
              {user?.name?.[0] || 'U'}
            </div>
            <div className={`transition-all duration-300 min-w-0 ${isSidebarCollapsed ? 'w-0 opacity-0 hidden' : 'flex-1 opacity-100 block'}`}>
              <p className="text-xs font-bold truncate text-textPrimary">{user?.name}</p>
              <p className="text-[9px] text-textSecondary truncate font-medium uppercase tracking-wider">{t('profile.verified') || 'Operator Verified'}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className={`w-full flex items-center font-bold text-red-600 hover:bg-red-50 rounded-xl transition-all duration-300 group
             ${isSidebarCollapsed ? 'justify-center p-3 text-center' : 'px-4 py-3 gap-3 text-xs'}`}
            title={isSidebarCollapsed ? t('common.logout') : ''}
          >
            <LogOut size={18} className="shrink-0 transition-transform duration-300 group-hover:-translate-x-1" />
            <span className={`whitespace-nowrap transition-all duration-300 ${isSidebarCollapsed ? 'w-0 opacity-0 hidden' : 'w-auto opacity-100 block'}`}>
              {t('common.logout')}
            </span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className={`flex-1 flex flex-col min-w-0 overflow-hidden transition-all duration-300 ease-in-out ${isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-[240px]'}`}>
        {/* Top Navbar */}
        <header className="h-16 bg-card border-b border-border flex items-center justify-between px-8 z-40">
          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(!isSidebarOpen)} className="lg:hidden p-2 hover:bg-background rounded-lg">
              <Menu size={20} />
            </button>
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-bold text-textPrimary capitalize tracking-tight">{t(`nav.${activeTab}`)}</h2>
              <span className="text-border">|</span>
              <p className="text-xs text-textSecondary font-medium">
                {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-[10px] font-bold uppercase tracking-widest transition-all duration-300 ${systemStatus === 'online'
              ? 'bg-primarySubtle text-primary border-primary/20'
              : 'bg-red-50 text-red-600 border-red-100'
              }`}>
              <div className={`w-1.5 h-1.5 rounded-full ${systemStatus === 'online' ? 'bg-primary' : 'bg-red-600 animate-pulse'}`} />
              {systemStatus === 'online' ? t('common.status_online') : t('common.status_offline')}
            </div>

            <div className="w-px h-6 bg-background/50 mx-2" />
            <LanguageSelector />
            <div className="w-px h-6 bg-background/50 mx-2" />

            <button
              onClick={() => setShowDebugConsole(!showDebugConsole)}
              className={`p-2 rounded-xl transition-all duration-200 border shadow-sm flex items-center gap-1.5 ${showDebugConsole ? 'bg-primary text-white border-primary border-primary' : 'bg-background text-textSecondary hover:text-primary border-border'}`}
              title="Toggle Debug Console"
            >
              <Terminal size={18} />
            </button>

            <div className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative p-2.5 bg-background rounded-xl text-textSecondary hover:text-primary transition-all duration-200 shadow-sm border border-border"
              >
                <Bell size={20} />
                {alerts.filter(a => !a.resolved).length > 0 && (
                  <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-600 text-[9px] font-bold text-white shadow-sm ring-2 ring-white">
                    {alerts.filter(a => !a.resolved).length}
                  </span>
                )}
              </button>

              {showNotifications && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setShowNotifications(false)}></div>
                  <div className="absolute right-0 mt-3 w-80 bg-card border border-border rounded-xl shadow-lg z-50 overflow-hidden animate-fadeIn flex flex-col max-h-[400px]">
                    <div className="p-3 border-b border-border bg-background flex justify-between items-center shrink-0">
                      <p className="text-xs font-bold text-textPrimary uppercase tracking-widest">Notifications</p>
                      <span className="text-[10px] font-bold bg-background/50 px-2 py-0.5 rounded-full text-textSecondary">
                        {alerts.filter(a => !a.resolved).length} Unresolved
                      </span>
                    </div>

                    <div className="overflow-y-auto flex-1 p-2 space-y-2">
                      {alerts.length === 0 ? (
                        <div className="p-6 text-center text-textSecondary text-xs">No alerts received.</div>
                      ) : (
                        alerts.slice(0, 5).map(alert => {
                          let styleClasses = '';
                          let IconComp = Activity;

                          if (alert.resolved) {
                            styleClasses = 'opacity-50 bg-background border-transparent text-textSecondary line-through';
                            IconComp = Activity;
                          } else if (alert.type === 'critical') {
                            styleClasses = 'bg-red-50 border-red-100 border-l-4 border-l-red-600 text-red-600';
                            IconComp = AlertTriangle;
                          } else if (alert.type === 'warning') {
                            styleClasses = 'bg-amber-50 border-amber-100 text-amber-600';
                            IconComp = AlertCircle;
                          } else {
                            styleClasses = 'bg-background border-border text-textSecondary';
                            IconComp = Activity;
                          }

                          return (
                            <div key={alert.id} className={`p-3 rounded-lg border flex gap-3 ${styleClasses}`}>
                              <div className="shrink-0 mt-0.5">
                                <IconComp size={16} className={
                                  alert.resolved ? 'text-textSecondary' :
                                    alert.type === 'critical' ? 'text-red-600' :
                                      alert.type === 'warning' ? 'text-amber-500' :
                                        'text-textSecondary'
                                } />
                              </div>
                              <div className="flex-1">
                                <p className="text-xs font-bold leading-tight">{alert.message}</p>
                                <div className="flex justify-between items-center mt-2">
                                  <span className="text-[9px] text-textSecondary uppercase tracking-widest">
                                    {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                  </span>
                                  {!alert.resolved && (
                                    <button
                                      onClick={() => handleResolveAlert(alert.id)}
                                      className="text-[9px] font-bold text-primary uppercase hover:underline"
                                    >
                                      Resolve
                                    </button>
                                  )}
                                </div>
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  </div>
                </>
              )}
            </div>

            <div className="w-px h-6 bg-background/50 mx-2" />
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <p className="text-xs font-bold text-textPrimary">{user?.name}</p>
                <p className="text-[10px] text-textSecondary">{user?.email}</p>
              </div>
              <button onClick={() => setActiveTab('profile')} className="w-9 h-9 bg-background rounded-full flex items-center justify-center border border-border hover:border-primary transition-colors">
                <UserIcon size={18} className="text-textSecondary" />
              </button>
            </div>
          </div>
        </header>

        {/* Scrollable Content */}
        <main className="flex-1 overflow-y-auto bg-background">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">


            {/* Tab Content */}
            <div className="relative min-h-[600px]">
              {/* Dashboard */}
              {activeTab === 'dashboard' && (
                <div className="animate-fadeIn space-y-12 pb-20">
                  {/* Header */}
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-border pb-8">
                    <div>
                      <h3 className="text-3xl font-black text-textPrimary tracking-tight">{t('dashboard.title')}</h3>
                      <p className="text-sm text-textSecondary mt-1 font-medium">{t('dashboard.subtitle')}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <select
                        value={globalZone}
                        onChange={(e) => setGlobalZone(e.target.value)}
                        className="bg-card border border-border rounded-xl px-5 py-2.5 text-xs font-bold text-textPrimary uppercase tracking-widest focus:border-primary outline-none shadow-sm cursor-pointer hover:border-primary transition-all"
                      >
                        <option value="all">All Zones</option>
                        {(dashboardData?.zones || []).map((zone) => (
                          <option key={zone.id} value={String(zone.id)}>
                            {zone.name}
                          </option>
                        ))}
                      </select>
                      <button className="bg-card border border-border text-textPrimary px-5 py-2.5 rounded-xl text-xs font-bold hover:bg-background transition-all flex items-center gap-2 shadow-sm">
                        <FileText size={16} />
                        {t('dashboard.tactical_report')}
                      </button>
                    </div>
                  </div>

                  {/* 1. TOP ROW: Health + KPIs */}
                  <section className="space-y-6">
                    <div className="flex items-center gap-2">
                      <Zap size={16} className="text-textSecondary" />
                      <h4 className="text-[10px] font-black text-textSecondary uppercase tracking-[0.2em]">Efficiency & Health</h4>
                    </div>
                    {metricsError ? (
                      <SectionError message="Failed to load KPI Metrics" onRetry={() => fetchDashboardData(true)} className="py-12" />
                    ) : (metricsLoading && !dashboardData) ? (
                      <KpiSkeleton />
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 items-start">
                        <KpiCard
                          icon={Droplets}
                          label={t('dashboard.kpi.humidity')}
                          value={dashboardData?.metrics?.humidity?.value !== undefined ? `${dashboardData.metrics.humidity.value}%` : '--'}
                          trend={dashboardData?.metrics?.humidity?.trend ?? 0}
                          status={dashboardData?.metrics?.humidity?.status || 'normal'}
                        />
                        <KpiCard
                          icon={Thermometer}
                          label={t('dashboard.kpi.temp')}
                          value={dashboardData?.metrics?.temperature?.value !== undefined ? `${dashboardData.metrics.temperature.value}°C` : '--'}
                          trend={dashboardData?.metrics?.temperature?.trend ?? 0}
                          status={dashboardData?.metrics?.temperature?.status || 'normal'}
                        />
                        <KpiCard
                          icon={Sprout}
                          label={t('dashboard.kpi.soil_moisture')}
                          value={dashboardData?.metrics?.soil_moisture?.value !== undefined ? `${dashboardData.metrics.soil_moisture.value}%` : '--'}
                          trend={dashboardData?.metrics?.soil_moisture?.trend ?? 0}
                          status={dashboardData?.metrics?.soil_moisture?.status || 'normal'}
                        />
                        <KpiCard
                          icon={Cylinder}
                          label={t('dashboard.kpi.water_tank')}
                          value={dashboardData?.metrics?.water_level?.value !== undefined ? `${dashboardData.metrics.water_level.value}%` : '--'}
                          trend={dashboardData?.metrics?.water_level?.trend ?? 0}
                          status={dashboardData?.metrics?.water_level?.status || 'normal'}
                        />
                        {healthError ? (
                          <div className="bg-red-50 rounded-xl border border-red-100 flex items-center justify-center p-4 min-h-[170px]">
                            <span className="text-[10px] font-bold text-red-600 uppercase">Health Error</span>
                          </div>
                        ) : (healthLoading && !farmHealth) ? (
                          <Skeleton className="min-h-[170px]" />
                        ) : (
                          farmHealth && <HealthAlertCard data={farmHealth} />
                        )}
                      </div>
                    )}
                  </section>

                  {/* 2. MIDDLE ROW: Analytics */}
                  <section className="space-y-6">
                    <div className="flex items-center gap-2">
                      <TrendingUp size={16} className="text-textSecondary" />
                      <h4 className="text-[10px] font-black text-textSecondary uppercase tracking-[0.2em]">Live Analytics</h4>
                    </div>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                      {analyticsError ? (
                        <SectionError message="Failed to load Moisture Analytics" onRetry={() => fetchDashboardData(true)} className="h-[300px] flex flex-col items-center justify-center" />
                      ) : (analyticsLoading && !analyticsData) ? (
                        <Skeleton className="h-[300px]" />
                      ) : (
                        <ChartCard title="Soil Moisture Trends (Last 7 Days)" icon={Droplets}>
                          {analyticsData?.moisture && analyticsData.moisture.labels?.length > 0 ? (
                            <SectionErrorBoundary sectionName="Soil Moisture Trends Chart">
                              <Suspense fallback={<ChartSkeleton />}>
                                <LazyLine
                                  data={analyticsData.moisture}
                                  options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: { legend: { display: false } },
                                    scales: {
                                      y: { display: true, grid: { color: 'rgba(0,0,0,0.05)' } },
                                      x: { display: true, grid: { display: false } }
                                    }
                                  }}
                                />
                              </Suspense>
                            </SectionErrorBoundary>
                          ) : (
                            <div className="w-full h-full min-h-[200px] flex flex-col items-center justify-center text-textSecondary">
                              <AlertCircle size={24} className="mb-2 opacity-20" />
                              <span className="text-[10px] font-bold uppercase tracking-widest">No sensor data available yet.</span>
                            </div>
                          )}
                        </ChartCard>
                      )}

                      {analyticsError ? (
                        <SectionError message="Failed to load Temperature Trends" onRetry={() => fetchDashboardData(true)} className="h-[300px] flex flex-col items-center justify-center" />
                      ) : (analyticsLoading && !analyticsData) ? (
                        <Skeleton className="h-[300px]" />
                      ) : (
                        <ChartCard title="Temperature Trends" icon={Thermometer}>
                          {analyticsData?.temperature && analyticsData.temperature.labels?.length > 0 ? (
                            <SectionErrorBoundary sectionName="Temperature Trends Chart">
                              <Suspense fallback={<ChartSkeleton />}>
                                <LazyArea
                                  data={analyticsData.temperature}
                                  options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: { legend: { display: false } },
                                    scales: {
                                      y: { display: true, grid: { color: 'rgba(0,0,0,0.05)' } },
                                      x: { display: true, grid: { display: false } }
                                    }
                                  }}
                                />
                              </Suspense>
                            </SectionErrorBoundary>
                          ) : (
                            <div className="w-full h-full min-h-[200px] flex flex-col items-center justify-center text-textSecondary">
                              <AlertCircle size={24} className="mb-2 opacity-20" />
                              <span className="text-[10px] font-bold uppercase tracking-widest">No sensor data available yet.</span>
                            </div>
                          )}
                        </ChartCard>
                      )}
                    </div>
                  </section>

                  {/* 3. BELOW: Zones & Control */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Side: Control and Mini Map */}
                    <div className="lg:col-span-2 space-y-8">
                      {/* Zone Overview Cards */}
                      <section className="space-y-6">
                        <div className="flex items-center gap-2">
                          <MapPin size={16} className="text-textSecondary" />
                          <h4 className="text-[10px] font-black text-textSecondary uppercase tracking-[0.2em]">Zone Status Matrix</h4>
                        </div>
                        {metricsError ? (
                          <SectionError message="Failed to load Zone Overview" onRetry={() => fetchDashboardData(true)} />
                        ) : metricsLoading && !dashboardData ? (
                          <ZoneOverviewSkeleton />
                        ) : (
                          <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
                            {(dashboardData?.zones || []).map(zone => {
                              const zoneStatus = String(zone.status || 'normal').toLowerCase();
                              const zoneMode = zone.mode || 'Manual';
                              const updatedTime = zone.last_updated
                                ? new Date(zone.last_updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                : '--';
                              return (
                              <div
                                key={zone.id}
                                onClick={() => {
                                  setGlobalZone(String(zone.id));
                                  setSelectedZone(String(zone.id));
                                }}
                                className={`bg-card rounded-xl border p-4 cursor-pointer transition-all hover:shadow-sm
                                      ${String(globalZone) === String(zone.id) ? 'border-primary ring-1 ring-primarySubtle/50 bg-primarySubtle' : 'border-border hover:border-primary'}
                                    `}
                              >
                                <div className="flex items-center justify-between mb-3">
                                  <h5 className="text-[9px] font-black text-textPrimary uppercase tracking-widest truncate mr-1">{zone.name}</h5>
                                  <div className={`w-2 h-2 rounded-full shrink-0 ${zoneStatus === 'critical' ? 'bg-red-600 animate-pulse' : zoneStatus === 'warning' ? 'bg-amber-500' : 'bg-primary'}`} />
                                </div>
                                <div className="space-y-3">
                                  <div className="flex items-end justify-between">
                                    <p className="text-2xl font-black tracking-tighter text-textPrimary">{zone.moisture ?? '--'}%</p>
                                    <span className="text-[8px] font-bold text-textSecondary uppercase tracking-widest bg-background px-1.5 py-0.5 rounded">MSTR</span>
                                  </div>
                                  <div className="flex items-center justify-between text-[8px] font-black uppercase tracking-widest border-t border-border pt-3">
                                    <span className={zoneMode === 'Auto' ? 'text-primary' : 'text-amber-500'}>{zoneMode}</span>
                                    <span className="text-textSecondary flex items-center gap-1"><Clock size={10} /> {updatedTime}</span>
                                  </div>
                                </div>
                              </div>
                              );
                            })}
                          </div>
                        )}
                      </section>

                      {/* Irrigation Control Panel */}
                      <IrrigationControl
                        selectedZone={selectedZone}
                        onZoneChange={setSelectedZone}
                        isAuto={isAutoMode}
                        onToggleMode={setIsAutoMode}
                        isIrrigating={isIrrigating}
                        onControl={handleIrrigationControl}
                        flowRate={flowRate}
                        onFlowChange={setFlowRate}
                        waterUsage={waterUsage}
                        timer={irrigationTimer}
                      />
                    </div>

                    {/* Right Side: Global Weather & Intelligence */}
                    <div className="space-y-8">
                      <WeatherCard data={dashboardData?.weather || { location: 'Farm-wide', temp: 28.4, humidity: 64, wind: 12.5 }} />

                      {/* Mini Zone Overview / Map Visual */}
                      <div className="bg-card rounded-xl border border-border p-6 shadow-sm">
                        <div className="flex items-center justify-between mb-6">
                          <h4 className="text-[10px] font-bold text-textSecondary uppercase tracking-widest flex items-center gap-2">
                            <Map size={14} className="text-textSecondary" />
                            Interactive Surface Map
                          </h4>
                          <span className="text-[9px] font-bold text-textSecondary uppercase tracking-widest">{dashboardData?.zones?.length || 5} Zones</span>
                        </div>
                        <div className="grid grid-cols-5 gap-3">
                          {(dashboardData?.zones || []).map((zoneData) => {
                            const zoneId = String(zoneData.id);
                            const isSelected = String(selectedZone) === zoneId || String(globalZone) === zoneId;
                            const status = String(zoneData.status || 'normal').toLowerCase();

                            return (
                              <div key={zoneId}
                                onClick={() => {
                                  setSelectedZone(zoneId);
                                  setGlobalZone(zoneId);
                                }}
                                className={`aspect-square rounded-lg border flex flex-col items-center justify-center gap-1 transition-all cursor-pointer
                                  ${isSelected ? 'bg-primarySubtle border-primary scale-105 z-10' : 'bg-background border-border opacity-70 hover:opacity-100'}`}>
                                <span className={`text-[10px] font-black ${isSelected ? 'text-primary' : 'text-textPrimary'}`}>Z{zoneId}</span>
                                <div className={`w-1.5 h-1.5 rounded-full ${status === 'critical' ? 'bg-red-600 animate-pulse' : status === 'warning' ? 'bg-amber-500' : 'bg-primary'}`} />
                              </div>
                            );
                          })}
                        </div>
                      </div>

                      {/* Intelligence Card */}
                      <div className="bg-card rounded-xl border border-border p-6 shadow-sm relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-1 opacity-5 group-hover:opacity-10 transition-opacity">
                          <ShieldCheck size={80} className="text-textSecondary/20" />
                        </div>
                        <div className="flex items-center gap-2 mb-6">
                          <div className="w-6 h-6 rounded bg-background flex items-center justify-center border border-border/50">
                            <ShieldCheck size={14} className="text-textSecondary" />
                          </div>
                          <h4 className="font-bold text-textPrimary uppercase tracking-widest text-[10px]">AgriPulse Intelligence</h4>
                        </div>
                        <p className="text-xs leading-relaxed text-textSecondary mb-6 font-medium relative z-10">
                          Nitrogen levels in North Sector are trending downwards.
                          <span className="block mt-2 font-bold text-textPrimary">Adjust fertilizer mix by +5% in next cycle.</span>
                        </p>
                        <button className="w-full py-3 bg-primary text-white rounded-xl text-[9px] font-black uppercase tracking-widest hover:bg-primaryHover transition-all shadow-sm relative z-10">
                          Deploy Recommendation
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* 4. BOTTOM ROW: Alerts / Activity */}
                  <section className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Activity size={16} className="text-textSecondary" />
                        <h4 className="text-[10px] font-black text-textSecondary uppercase tracking-[0.2em]">{t('dashboard.activity.title')}</h4>
                      </div>
                      <button className="bg-card border border-border text-textPrimary px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-background transition-all shadow-sm">{t('reports.view_all')}</button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {[
                        { title: 'Irrigation Pattern Optimized', zone: 'Zone 4-A', time: '12 mins ago', type: 'System', desc: 'Flow rate adjusted based on moisture drop.' },
                        { title: 'Pathology Scan Completed', zone: 'Sector 7', time: '1 hour ago', type: 'AI', desc: 'No active pathology found in manual scan.' },
                        { title: 'Humidity Threshold Alert', zone: 'Greenhouse B', time: '3 hours ago', type: 'Alert', desc: 'Critical humidity level detected (> 85%).' }
                      ].map((log, i) => (
                        <div key={i} className="bg-card border border-border rounded-xl p-5 hover:border-primary transition-all group">
                          <div className="flex items-center justify-between mb-4">
                            <div className={`px-2 py-1 rounded text-[8px] font-black uppercase tracking-widest 
                                ${log.type === 'Alert' ? 'bg-red-50 text-red-600' : log.type === 'AI' ? 'bg-background text-primary border border-primary/20' : 'bg-background text-textSecondary border border-border'}`}>
                              {log.type}
                            </div>
                            <span className="text-[9px] font-bold text-textSecondary uppercase tracking-widest">{log.time}</span>
                          </div>
                          <h5 className="text-sm font-bold text-textPrimary mb-1 transition-colors">{log.title}</h5>
                          <p className="text-[10px] text-textSecondary font-medium mb-4">{log.zone}</p>
                          <p className="text-xs text-textSecondary leading-relaxed">{log.desc}</p>
                        </div>
                      ))}
                    </div>
                  </section>
                </div>
              )}

              {/* Disease Scanner */}
              {
                activeTab === 'disease' && (
                  <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 animate-fadeIn">
                    <div className="lg:col-span-3 dashboard-card flex flex-col items-center justify-center min-h-[500px] relative overflow-hidden group">
                      <div className="absolute top-0 left-0 w-full h-1 bg-background" />

                      {previewImage ? (
                        <div className="w-full h-full flex flex-col items-center p-4">
                          <div className="relative group_img max-w-lg w-full">
                            <img src={previewImage} className="w-full rounded-2xl shadow-sm border border-border" alt="Leaf Preview" />
                            <button
                              onClick={() => {
                                scanRequestIdRef.current += 1;
                                setScannerLoading(false);
                                setPreviewImage(null);
                                setDiseaseResult(null);
                                startCamera();
                              }}
                              className="absolute -top-3 -right-3 bg-red-600 text-white p-2 rounded-xl shadow-sm hover:bg-red-700 transition-colors"
                            >
                              <X size={16} />
                            </button>
                          </div>
                          <p className="text-sm text-textSecondary font-medium mt-6">{t('scanner.ready')}</p>
                        </div>
                      ) : isCameraActive ? (
                        <div className="w-full h-full flex flex-col items-center justify-center p-4 relative">
                          <video
                            ref={videoRef}
                            autoPlay
                            playsInline
                            className="w-full max-w-lg rounded-2xl shadow-sm border border-border bg-black object-cover aspect-[4/3]"
                          />
                          <button
                            onClick={captureImage}
                            disabled={scannerLoading}
                            className="absolute bottom-10 bg-primary text-white p-4 rounded-full hover:bg-primaryHover transition-transform shadow-lg hover:scale-105 active:scale-95 disabled:opacity-50"
                          >
                            {scannerLoading ? <Loader2 className="animate-spin" size={24} /> : <Camera size={24} />}
                          </button>
                          <button
                            onClick={stopCamera}
                            className="absolute top-6 right-6 bg-card/80 backdrop-blur text-textSecondary p-2 rounded-xl hover:text-textPrimary hover:bg-background transition-all"
                          >
                            <X size={16} />
                          </button>
                        </div>
                      ) : (
                        <div className="text-center p-12 w-full max-w-md mx-auto">
                          <div className="w-20 h-20 bg-background rounded-3xl flex items-center justify-center mx-auto mb-6 border border-border/50 group-hover:scale-105 transition-transform shadow-sm">
                            <Camera size={32} className="text-textSecondary" />
                          </div>
                          <h3 className="text-2xl font-bold text-textPrimary tracking-tight">{t('scanner.title')}</h3>
                          <p className="text-textSecondary text-sm mt-2 mb-8 leading-relaxed max-w-[280px] mx-auto">{t('scanner.subtitle')}</p>

                          {cameraError && (
                            <div className="mb-6 p-4 bg-red-50/50 border border-red-100/50 rounded-xl text-xs text-red-600 font-medium flex items-start gap-2 text-left">
                              <AlertCircle size={14} className="shrink-0 mt-0.5" />
                              <p>{cameraError}</p>
                            </div>
                          )}

                          <div className="flex flex-col gap-3 w-full sm:w-fit mx-auto">
                            <button
                              onClick={startCamera}
                              className="bg-primary text-white px-8 py-3.5 rounded-xl font-bold text-sm hover:bg-primaryHover transition-all shadow-sm flex items-center justify-center gap-2 w-full"
                            >
                              <Camera size={18} />
                              Open Camera
                            </button>

                            <label className="bg-background text-textPrimary border border-border px-8 py-3.5 rounded-xl font-bold text-sm cursor-pointer hover:border-primary transition-all shadow-sm flex items-center justify-center gap-2 w-full">
                              {scannerLoading ? <Loader2 className="animate-spin" size={18} /> : <ArrowRight size={18} />}
                              {scannerLoading ? t('scanner.btn_analyzing') : "Upload from Device"}
                              <input type="file" className="hidden" accept="image/*" capture="environment" onChange={handleImageUpload} disabled={scannerLoading} />
                            </label>
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="lg:col-span-2 space-y-6">
                      <div className="dashboard-card h-full flex flex-col">
                        <div className="flex items-center gap-2 text-[10px] font-bold text-textSecondary uppercase tracking-widest mb-6">
                          <Activity size={14} className="text-textSecondary" />
                          {t('scanner.output')}
                        </div>

                        {scannerLoading ? (
                          <div className="flex-1 flex flex-col items-center justify-center text-center py-20">
                            <Loader2 size={40} className="mb-4 text-textSecondary animate-spin" />
                            <p className="text-sm font-bold text-textSecondary uppercase tracking-widest">
                              {t('scanner.btn_analyzing') || 'Analyzing...'}
                            </p>
                          </div>
                        ) : diseaseResult ? (
                          <div className="space-y-8 flex-1">
                            <div>
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="text-2xl font-bold text-textPrimary">{diseaseResult.prediction}</h4>
                                <span className="bg-primarySubtle text-primary text-[10px] font-black px-2 py-1 rounded-md border border-primary/20">VERIFIED</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <div className="flex-1 h-1.5 bg-background rounded-full overflow-hidden">
                                  <div className="h-full bg-primary" style={{ width: `${diseaseResult.confidence * 100}%` }} />
                                </div>
                                <span className="text-xs font-bold text-textSecondary">{(diseaseResult.confidence * 100).toFixed(0)}%</span>
                              </div>
                            </div>

                            <div className="space-y-4">
                              <div className="bg-background p-4 rounded-xl border border-border">
                                <p className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mb-2">Recommended Protocol</p>
                                <p className="text-sm text-textPrimary leading-relaxed">
                                  {diseaseResult.treatment_suggestion || 'No active pathology detected. System recommends continued monitoring of hydration and nutrient levels.'}
                                </p>
                              </div>

                              <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 bg-background rounded-xl border border-border">
                                  <p className="text-[10px] font-bold text-textSecondary uppercase mb-1">Risk Level</p>
                                  <p className={`text-sm font-bold ${diseaseResult.prediction.toLowerCase().includes('healthy') ? 'text-primary' : 'text-orange-600'}`}>
                                    {diseaseResult.prediction.toLowerCase().includes('healthy') ? 'Standard' : 'Elevated'}
                                  </p>
                                </div>
                                <div className="p-4 bg-background rounded-xl border border-border">
                                  <p className="text-[10px] font-bold text-textSecondary uppercase mb-1">Response</p>
                                  <p className="text-sm font-bold text-textPrimary">Automated</p>
                                </div>
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="flex-1 flex flex-col items-center justify-center text-center py-20 opacity-40">
                            <AlertCircle size={40} className="mb-4 text-textSecondary" />
                            <p className="text-sm font-bold text-textSecondary uppercase tracking-widest">Awaiting Input Data</p>
                          </div>
                        )}

                        <div className="mt-auto pt-8 border-t border-border">
                          <p className="text-[10px] text-textSecondary leading-relaxed">
                            Enterprise AI Diagnostic v4.2.0 ??? Cross-referenced with Global Pathology Database
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              }

              {/* Smart Irrigation */}
              {
                activeTab === 'irrigation' && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fadeIn items-start">
                    <div className="lg:col-span-2 dashboard-card">
                      <div className="flex items-center gap-4 mb-8 pb-6 border-b border-border">
                        <div className="bg-background p-3 rounded-xl border border-border/50">
                          <Droplets className="text-textSecondary" size={24} />
                        </div>
                        <div>
                          <h2 className="text-xl font-black text-textPrimary tracking-tight">{t('irrigation.title')}</h2>
                          <p className="text-textSecondary text-[10px] font-black uppercase tracking-widest mt-1">{t('irrigation.subtitle')}</p>
                        </div>
                      </div>

                      <div className="mb-10 bg-background rounded-xl p-8 border border-border">
                        <IrrigationVisual moisture={irrigationData.soil_moisture_pct} />
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                        <div className="space-y-8">
                          <div>
                            <div className="flex justify-between mb-3 items-end">
                              <label className="text-[10px] font-black uppercase tracking-widest text-textSecondary">{t('irrigation.moisture_cap')}</label>
                              <span className="text-textPrimary font-black text-lg">{irrigationData.soil_moisture_pct}%</span>
                            </div>
                            <input
                              type="range"
                              min="0" max="100"
                              value={irrigationData.soil_moisture_pct}
                              onChange={(e) => setIrrigationData({ ...irrigationData, soil_moisture_pct: parseInt(e.target.value) })}
                              className="w-full accent-primary h-1.5 bg-background rounded-full appearance-none cursor-pointer"
                            />
                          </div>
                          <div>
                            <div className="flex justify-between mb-3 items-end">
                              <label className="text-[10px] font-black uppercase tracking-widest text-textSecondary">{t('irrigation.ambient_thermal')}</label>
                              <span className="text-textPrimary font-black text-lg">{irrigationData.temperature_c}??C</span>
                            </div>
                            <input
                              type="range"
                              min="0" max="50"
                              value={irrigationData.temperature_c}
                              onChange={(e) => setIrrigationData({ ...irrigationData, temperature_c: parseInt(e.target.value) })}
                              className="w-full accent-primary h-1.5 bg-background rounded-full appearance-none cursor-pointer"
                            />
                          </div>
                        </div>

                        <div className="space-y-6">
                          <div>
                            <label className="block text-[10px] font-black uppercase tracking-widest text-textSecondary mb-3">{t('irrigation.crop_class')}</label>
                            <div className="relative">
                              <select
                                value={irrigationData.crop_type}
                                onChange={(e) => setIrrigationData({ ...irrigationData, crop_type: e.target.value })}
                                className="w-full bg-background border border-border rounded-xl p-3.5 text-xs font-bold text-textPrimary focus:border-primary outline-none transition-all appearance-none cursor-pointer shadow-sm"
                              >
                                <option value="tomato">Solanum Lycopersicum</option>
                                <option value="potato">Solanum Tuberosum</option>
                                <option value="rice">Oryza Sativa</option>
                                <option value="wheat">Triticum Aestivum</option>
                                <option value="maize">Zea Mays</option>
                              </select>
                              <div className="absolute right-4 top-1_2 -translate-y-1_2 pointer-events-none opacity-40">
                                <ChevronDown size={14} />
                              </div>
                            </div>
                          </div>

                          <button
                            onClick={handleIrrigationSubmit}
                            disabled={loading}
                            className="w-full bg-primary text-white font-black py-4 rounded-xl flex items-center justify-center gap-3 hover:bg-primaryHover transition-all shadow-sm text-xs uppercase tracking-widest"
                          >
                            {loading ? <Loader2 className="animate-spin" size={16} /> : <Activity size={16} />}
                            {loading ? 'CALCULATING...' : 'EXECUTE ANALYSIS'}
                          </button>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-6 lg:h-full">
                      <div className="dashboard-card h-full flex flex-col items-center justify-center min-h-[400px] border-dashed border-2 bg-background">
                        {irrigationResult ? (
                          <div className="text-center animate-fadeIn w-full px-6">
                            <div className="w-16 h-16 bg-background rounded-full flex items-center justify-center mx-auto mb-6 border border-border/50">
                              <CheckCircle2 size={32} className="text-textSecondary" />
                            </div>
                            <p className="text-[10px] text-textSecondary uppercase font-bold tracking-[0.2em] mb-2">Optimal Load</p>
                            <h3 className="text-5xl font-black text-textPrimary tracking-tight mb-2">
                              {irrigationResult.recommended_liters}
                              <span className="text-lg text-textSecondary font-bold ml-2">LITERS</span>
                            </h3>
                            <div className="mt-8 pt-8 border-t border-border w-full">
                              <div className="flex items-center justify-between text-xs mb-3">
                                <span className="text-textSecondary font-medium">Growth Phase</span>
                                <span className="text-textPrimary font-bold uppercase">{irrigationData.growth_stage}</span>
                              </div>
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-textSecondary font-medium">Watering Window</span>
                                <span className="text-textPrimary font-bold uppercase">12:00 MINS</span>
                              </div>
                            </div>
                            <button className="w-full bg-primary text-white font-bold py-3 rounded-xl mt-10 hover:bg-primaryHover transition-all text-sm uppercase tracking-wider shadow-sm">
                              Deploy System
                            </button>
                          </div>
                        ) : (
                          <div className="text-center flex flex-col items-center justify-center opacity-30 select-none">
                            <div className="w-16 h-16 rounded-full border-2 border-slate-300 flex items-center justify-center mb-6">
                              <Activity size={32} className="text-textSecondary" />
                            </div>
                            <p className="text-xs font-bold uppercase tracking-widest text-textSecondary">Awaiting Calibration Parameters</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )
              }

              {/* Field Reports */}
              {
                activeTab === 'reports' && (
                  <div className="animate-fadeIn space-y-8">
                    <div className="flex items-center justify-between mb-8">
                      <div>
                        <h3 className="text-2xl font-bold text-textPrimary">{t('reports.title')}</h3>
                        <p className="text-sm text-textSecondary mt-1">{t('reports.subtitle')}</p>
                      </div>
                      <div className="flex gap-3">
                        <button className="px-4 py-2 bg-card border border-border rounded-lg text-xs font-bold text-textPrimary hover:bg-background transition-colors flex items-center gap-2 shadow-sm">
                          {t('reports.btn_csv')}
                        </button>
                        <button className="bg-card border border-border text-textPrimary px-4 py-2 rounded-lg text-xs font-bold hover:bg-background transition-colors flex items-center gap-2 shadow-sm">
                          {t('reports.btn_pdf')}
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                      {[
                        { label: 'Total Water Usage', value: '12,450L', change: '-12%', icon: Droplets, color: 'text-blue-600', trendPos: false },
                        { label: 'Avg Soil Health', value: '88/100', change: '+4%', icon: Sprout, color: 'text-textSecondary', trendPos: true },
                        { label: 'Active Alerts', value: '2', change: '0', icon: AlertCircle, color: 'text-orange-600', trendPos: null }
                      ].map((stat, i) => (
                        <div key={i} className="dashboard-card">
                          <div className="flex items-center gap-3 mb-6">
                            <div className={`p-2.5 rounded-lg bg-background ${stat.color}`}>
                              <stat.icon size={20} />
                            </div>
                            <span className="text-[10px] font-black text-textSecondary uppercase tracking-[0.15em]">{t(`irrigation.stats.${stat.label.toLowerCase().replace(' ', '/')}`) || stat.label}</span>
                          </div>
                          <div className="flex items-end justify-between">
                            <h4 className="text-3xl font-black text-textPrimary tracking-tight">{stat.value}</h4>
                            <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${stat.trendPos === true ? 'bg-primarySubtle text-primary' : stat.trendPos === false ? 'bg-red-50 text-red-600' : 'bg-background text-textSecondary'}`}>
                              {stat.change}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="dashboard-card shadow-none bg-background border-dashed">
                      <div className="flex items-center justify-between mb-6">
                        <h4 className="font-bold text-textPrimary">{t('reports.recent_title')}</h4>
                        <span className="text-[10px] font-bold text-primary uppercase cursor-pointer hover:underline">{t('reports.view_all')}</span>
                      </div>
                      <div className="space-y-3">
                        {[
                          { name: 'Weekly Resource Allocation', date: 'Feb 21 - Feb 28', status: 'Ready' },
                          { name: 'Monthly Pathology Trend', date: 'Jan 28 - Feb 28', status: 'Processing' },
                          { name: 'Soil Moisture Baseline v2', date: 'Feb 14 - Feb 21', status: 'Ready' }
                        ].map((report, i) => (
                          <div key={i} className="flex items-center justify-between p-4 bg-card rounded-xl border border-border">
                            <div className="flex items-center gap-4">
                              <FileText className="text-textSecondary" size={20} />
                              <div>
                                <p className="text-sm font-bold text-textPrimary">{report.name}</p>
                                <p className="text-[10px] text-textSecondary uppercase tracking-wider">{report.date}</p>
                              </div>
                            </div>
                            <span className={`text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-widest ${report.status === 'Ready' ? 'bg-primarySubtle text-primary' : 'bg-background text-textSecondary animate-pulse'}`}>
                              {report.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )
              }

              {/* User Profile */}
              {activeTab === 'profile' && <ProfileView user={user} />}

              {/* Alerts Page */}
              {
                activeTab === 'alerts' && (
                  <div className="animate-fadeIn max-w-6xl space-y-8 pb-20">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div>
                        <h3 className="text-2xl font-bold text-textPrimary">System Alerts</h3>
                        <p className="text-sm text-textSecondary mt-1">Review and manage farm notification history.</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <select
                          value={alertFilterType}
                          onChange={(e) => setAlertFilterType(e.target.value)}
                          className="bg-card border border-border rounded-xl px-4 py-2.5 text-xs font-bold text-textPrimary uppercase tracking-widest focus:border-primary outline-none"
                        >
                          <option value="all">All Types</option>
                          <option value="info">Info</option>
                          <option value="warning">Warning</option>
                          <option value="critical">Critical</option>
                        </select>
                        <select
                          value={alertFilterStatus}
                          onChange={(e) => setAlertFilterStatus(e.target.value)}
                          className="bg-card border border-border rounded-xl px-4 py-2.5 text-xs font-bold text-textPrimary uppercase tracking-widest focus:border-primary outline-none"
                        >
                          <option value="all">All Status</option>
                          <option value="unresolved">Unresolved</option>
                          <option value="resolved">Resolved</option>
                        </select>
                      </div>
                    </div>

                    <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
                      {filteredAlertsTab.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-16 text-textSecondary">
                          <CheckCircle2 size={48} className="mb-4 opacity-50" />
                          <p className="text-sm font-bold uppercase tracking-widest">No alerts found</p>
                        </div>
                      ) : (
                        <div className="divide-y divide-border">
                          {filteredAlertsTab.map(alert => (
                            <div key={alert.id} className={`p-5 flex flex-col md:flex-row gap-4 justify-between items-start md:items-center hover:bg-background transition-colors ${alert.resolved ? 'opacity-60' : ''}`}>
                              <div className="flex items-start gap-4">
                                <div className={`shrink-0 mt-1 p-2 rounded-lg ${alert.type === 'critical' ? 'bg-red-50 text-red-600' : alert.type === 'warning' ? 'bg-amber-50 text-amber-500' : 'bg-background text-textSecondary'}`}>
                                  {alert.type === 'critical' ? <AlertTriangle size={20} /> : alert.type === 'warning' ? <AlertCircle size={20} /> : <Activity size={20} />}
                                </div>
                                <div>
                                  <h4 className={`text-sm font-bold ${alert.type === 'critical' && !alert.resolved ? 'text-red-600' : 'text-textPrimary'}`}>{alert.message}</h4>
                                  <div className="flex items-center gap-3 mt-1.5 text-[10px] font-bold uppercase tracking-widest">
                                    <span className={alert.type === 'critical' ? 'text-red-500' : alert.type === 'warning' ? 'text-yellow-500' : 'text-blue-500'}>
                                      {alert.type}
                                    </span>
                                    <span className="text-border">|</span>
                                    <span className="text-textSecondary flex items-center gap-1">
                                      <Clock size={10} />
                                      {new Date(alert.timestamp).toLocaleString()}
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <div className="shrink-0 ml-12 md:ml-0 flex items-center gap-3">
                                {alert.resolved ? (
                                  <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-primarySubtle text-primary rounded-lg text-[10px] font-bold uppercase tracking-widest border border-primary/20">
                                    <Check size={12} />
                                    Resolved
                                  </span>
                                ) : (
                                  <button
                                    onClick={() => handleResolveAlert(alert.id)}
                                    className="px-4 py-2 bg-card border border-border text-textPrimary rounded-lg text-xs font-bold uppercase tracking-widest hover:bg-background transition-colors flex items-center gap-2 shadow-sm"
                                  >
                                    Mark Resolved
                                  </button>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )
              }

              {/* Settings Tab */}
              {
                activeTab === 'settings' && (
                  <div className="animate-fadeIn max-w-5xl space-y-8 pb-20">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-2xl font-bold text-textPrimary">{t('settings.title')}</h3>
                        <p className="text-sm text-textSecondary mt-1">{t('settings.subtitle')}</p>
                      </div>
                      <button
                        onClick={handleSaveSettings}
                        disabled={loading}
                        className="bg-primary text-white px-6 py-2.5 rounded-xl font-bold text-sm hover:bg-primaryHover transition-all shadow-sm flex items-center gap-2"
                      >
                        {loading ? <Loader2 size={16} className="animate-spin" /> : <Check size={16} />}
                        {t('common.save_changes') || 'Save Changes'}
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      {/* 1. Theme Settings */}
                      <div className="dashboard-card group">
                        <div className="flex items-center gap-3 mb-6">
                          <div className="p-2 bg-background rounded-lg text-textSecondary border border-border/50">
                            <Sun size={18} />
                          </div>
                          <div>
                            <h4 className="text-sm font-bold text-textPrimary">{t('settings.theme_title') || 'Theme Settings'}</h4>
                            <p className="text-[10px] text-textSecondary leading-relaxed">{t('settings.theme_desc') || 'Customize your visual experience and power consumption.'}</p>
                          </div>
                        </div>
                        <div className="grid grid-cols-3 gap-3">
                          {['light', 'dark', 'system'].map((tMode) => (
                            <button
                              key={tMode}
                              onClick={() => setTheme(tMode)}
                              className={`px-4 py-3 rounded-xl border text-[10px] font-bold uppercase tracking-widest transition-all
                              ${theme === tMode
                                  ? 'bg-primarySubtle border-primary text-primary shadow-sm'
                                  : 'bg-background border-border text-textSecondary hover:border-primary hover:text-textPrimary'}`}
                            >
                              {tMode}
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* 2. Language Settings */}
                      <div className="dashboard-card group">
                        <div className="flex items-center gap-3 mb-6">
                          <div className="p-2 bg-background rounded-lg text-textSecondary border border-border/50">
                            <Languages size={18} />
                          </div>
                          <div>
                            <h4 className="text-sm font-bold text-textPrimary">{t('settings.lang_title') || 'Language Settings'}</h4>
                            <p className="text-[10px] text-textSecondary leading-relaxed">{t('settings.lang_desc') || 'Select your preferred language for the interface.'}</p>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                          {LANGUAGE_OPTIONS.map((langOpt) => (
                            <button
                              key={langOpt.code}
                              onClick={() => {
                                i18n.changeLanguage(langOpt.code);
                                localStorage.setItem('agroguard_lang', langOpt.code);
                              }}
                              className={`flex-1 py-1.5 rounded-lg border text-[10px] font-bold uppercase tracking-widest transition-all
                                    ${i18n.language?.startsWith(langOpt.code) ? 'bg-primarySubtle border-primary text-primary shadow-sm' : 'bg-background border-border text-textSecondary'}`}
                            >
                              {langOpt.label} ({langOpt.short})
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )
              }
            </div>
          </div>
        </main>
        {
          showToast && (
            <Toast
              message={toastMessage}
              onClose={() => setShowToast(false)}
            />
          )
        }
      </div>
    </div>
  );
}

export default App;
