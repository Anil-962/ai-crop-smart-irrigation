import React, { useState, useEffect } from 'react';

const DebugConsole = ({ isVisible }) => {
    const [lastRequest, setLastRequest] = useState(null);

    useEffect(() => {
        const handleApiLog = (event) => {
            setLastRequest(event.detail);
        };

        window.addEventListener('api-debug-log', handleApiLog);

        return () => {
            window.removeEventListener('api-debug-log', handleApiLog);
        };
    }, []);

    if (!isVisible) return null;

    return (
        <div className="fixed bottom-4 right-4 w-96 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl overflow-hidden z-50 animate-in slide-in-from-bottom-5">
            <div className="bg-slate-800 px-4 py-3 flex items-center justify-between border-b border-slate-700">
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
                    <h3 className="text-sm font-semibold text-slate-200">API Debug Console</h3>
                </div>
                <span className="text-xs text-slate-400 font-mono">LIVE</span>
            </div>

            <div className="p-4 space-y-4">
                {!lastRequest ? (
                    <div className="text-sm text-slate-500 italic text-center py-4">
                        Waiting for API requests...
                    </div>
                ) : (
                    <>
                        <div className="space-y-1">
                            <label className="text-xs text-slate-500 font-medium uppercase tracking-wider">ENDPOINT</label>
                            <div className="flex items-center gap-2 bg-slate-800/50 p-2 rounded border border-slate-700/50">
                                <span className="text-xs font-bold text-blue-400 P-1 rounded bg-blue-500/10">
                                    {lastRequest.method}
                                </span>
                                <span className="font-mono text-sm text-slate-300 truncate" title={lastRequest.url}>
                                    {lastRequest.url}
                                </span>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <label className="text-xs text-slate-500 font-medium uppercase tracking-wider">STATUS</label>
                                <div className="flex items-center gap-2">
                                    <div className={`w-2 h-2 rounded-full ${lastRequest.status >= 200 && lastRequest.status < 300 ? 'bg-green-500' :
                                            lastRequest.status >= 400 ? 'bg-red-500' : 'bg-yellow-500'
                                        }`}></div>
                                    <span className={`font-mono font-medium ${lastRequest.status >= 200 && lastRequest.status < 300 ? 'text-green-400' :
                                            lastRequest.status >= 400 ? 'text-red-400' : 'text-yellow-400'
                                        }`}>
                                        {lastRequest.status || 'ERROR'}
                                    </span>
                                </div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs text-slate-500 font-medium uppercase tracking-wider">LATENCY</label>
                                <div className="font-mono text-sm text-slate-300">
                                    {lastRequest.duration} <span className="text-slate-500">ms</span>
                                </div>
                            </div>
                        </div>

                        {lastRequest.error && (
                            <div className="space-y-1 mt-2">
                                <label className="text-xs text-red-500/80 font-medium uppercase tracking-wider flex items-center gap-1">
                                    ERROR
                                </label>
                                <div className="bg-red-500/10 border border-red-500/20 rounded p-2 text-sm text-red-400 font-mono break-words">
                                    {lastRequest.error}
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

export default DebugConsole;
