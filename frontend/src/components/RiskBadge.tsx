import React from 'react';
import { AlertCircle, CheckCircle2, AlertTriangle, PackageX } from 'lucide-react';

interface RiskBadgeProps {
  status: 'HEALTHY' | 'LOW_STOCK' | 'STOCKOUT_RISK' | 'OVERSTOCK_RISK' | string;
  size?: 'sm' | 'md';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ status, size = 'sm' }) => {
  const pad = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';

  switch (status) {
    case 'STOCKOUT_RISK':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full font-semibold bg-red-500/10 text-red-400 border border-red-500/20 ${pad}`}>
          <AlertCircle className="w-3.5 h-3.5" />
          Stockout Risk
        </span>
      );
    case 'LOW_STOCK':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 ${pad}`}>
          <AlertTriangle className="w-3.5 h-3.5" />
          Low Stock
        </span>
      );
    case 'OVERSTOCK_RISK':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 ${pad}`}>
          <PackageX className="w-3.5 h-3.5" />
          Overstock Risk
        </span>
      );
    case 'HEALTHY':
    default:
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 ${pad}`}>
          <CheckCircle2 className="w-3.5 h-3.5" />
          Healthy
        </span>
      );
  }
};
