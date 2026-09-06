import React, { useState } from 'react';
import { UploadCloud, CheckCircle2, AlertCircle, FileText, Database, Info } from 'lucide-react';
import { api } from '../services/api';

export const DataUploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const res = await api.uploadCSV(file);
      setResult(res);
    } catch (err: any) {
      console.error('Upload failed:', err);
      const detail = err.response?.data?.detail;
      if (typeof detail === 'object' && detail.message) {
        setError(`${detail.message} ${detail.errors ? detail.errors.join(', ') : ''}`);
      } else {
        setError(detail || 'Failed to upload and validate CSV dataset.');
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl">
      {/* Upload Box */}
      <div className="glass-card rounded-2xl p-8 text-center border-dashed border-2 border-slate-700/80 hover:border-emerald-500/50 transition">
        <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto mb-4">
          <UploadCloud className="w-8 h-8" />
        </div>
        <h3 className="font-bold text-lg text-white mb-1">Upload Retail Sales Dataset (CSV)</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto mb-6">
          Upload custom historical transaction logs. The system will execute schema checks, null imputation, and time grid padding.
        </p>

        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="hidden"
          id="csv-upload"
        />
        <label
          htmlFor="csv-upload"
          className="px-6 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs transition cursor-pointer border border-slate-700 inline-block mb-4"
        >
          {file ? `Selected: ${file.name}` : 'Select CSV File'}
        </label>

        {file && (
          <div className="mt-4">
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="px-8 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition shadow-lg shadow-emerald-600/30 disabled:opacity-50"
            >
              {uploading ? 'Validating & Processing Dataset...' : 'Run Automated Preprocessing Pipeline'}
            </button>
          </div>
        )}
      </div>

      {/* Success Notification */}
      {result && (
        <div className="glass-card rounded-2xl p-6 border-emerald-500/30 bg-emerald-950/20">
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
            <div>
              <h4 className="font-bold text-white text-base">Dataset Successfully Validated & Ingested</h4>
              <p className="text-xs text-slate-400">{result.message}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4 pt-4 border-t border-slate-800">
            <div>
              <span className="text-[10px] text-slate-400 uppercase">Total Daily Rows</span>
              <p className="text-base font-bold text-white">{result.total_rows?.toLocaleString()}</p>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase">Stores Tracked</span>
              <p className="text-base font-bold text-emerald-400">{result.unique_stores}</p>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase">SKUs Tracked</span>
              <p className="text-base font-bold text-emerald-400">{result.unique_products}</p>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase">Date Span</span>
              <p className="text-xs font-mono text-slate-300">
                {result.date_range ? `${result.date_range[0]} to ${result.date_range[1]}` : 'N/A'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error Notification */}
      {error && (
        <div className="glass-card rounded-2xl p-6 border-red-500/30 bg-red-950/20 flex items-start gap-3">
          <AlertCircle className="w-6 h-6 text-red-400 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-bold text-white text-base">Validation Failed</h4>
            <p className="text-xs text-red-300 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Expected Schema Specification */}
      <div className="glass-card rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Info className="w-4 h-4 text-slate-400" />
          <h4 className="font-bold text-sm text-white">Required CSV Columns Specification</h4>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span className="font-mono text-emerald-400 font-bold">Date</span>
            <p className="text-[11px] text-slate-400 mt-1">YYYY-MM-DD string</p>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span className="font-mono text-emerald-400 font-bold">Store_ID</span>
            <p className="text-[11px] text-slate-400 mt-1">Unique store identifier</p>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span className="font-mono text-emerald-400 font-bold">Product_ID</span>
            <p className="text-[11px] text-slate-400 mt-1">Unique product SKU</p>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span className="font-mono text-emerald-400 font-bold">Units_Sold</span>
            <p className="text-[11px] text-slate-400 mt-1">Daily unit sales integer</p>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span className="font-mono text-emerald-400 font-bold">Price</span>
            <p className="text-[11px] text-slate-400 mt-1">Unit selling price float</p>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span className="font-mono text-emerald-400 font-bold">Category</span>
            <p className="text-[11px] text-slate-400 mt-1">Product category name</p>
          </div>
        </div>
      </div>
    </div>
  );
};
