import React, { useEffect } from 'react';
import { CheckCircle2, X } from 'lucide-react';

const Toast = ({ message, type = 'success', onClose, duration = 3000 }) => {
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, duration);
        return () => clearTimeout(timer);
    }, [onClose, duration]);

    return (
        <div className="fixed bottom-8 right-8 z-[100] animate-slideInRight">
            <div className={`flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-lg border border-border bg-white dark:bg-slate-800 ${type === 'success' ? 'border-l-4 border-l-primary' : 'border-l-4 border-l-red-500'
                }`}>
                {type === 'success' ? (
                    <CheckCircle2 size={18} className="text-primary" />
                ) : (
                    <X size={18} className="text-red-500" />
                )}
                <p className="text-sm font-bold text-textPrimary">{message}</p>
                <button onClick={onClose} className="ml-2 text-textSecondary hover:text-textPrimary transition-colors">
                    <X size={14} />
                </button>
            </div>
        </div>
    );
};

export default Toast;
