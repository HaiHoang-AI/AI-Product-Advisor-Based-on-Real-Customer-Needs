"use client";

import { ComparisonItem } from "./types";
import { Table, Check, Zap, Layers } from "lucide-react";

export function ComparisonView({ data }: { data: ComparisonItem[] }) {
  if (!data || data.length < 2) return null;

  // Extract all unique spec keys
  const allSpecKeys = Array.from(
    new Set(data.flatMap((item) => Object.keys(item.specs || {})))
  );

  const formatPrice = (price?: number) => {
    if (!price) return "—";
    return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(price);
  };

  return (
    <div className="organic-card overflow-hidden my-3 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
      {/* Table Header */}
      <div className="p-3.5 sm:p-4 bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          <h4 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
            Bảng So Sánh Thông Số Trực Quan (Top 3)
          </h4>
        </div>
        <span className="badge-eco text-[11px] py-0.5 px-2.5">
          {data.length} Sản phẩm
        </span>
      </div>

      {/* Responsive Horizontal Scroll Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30">
              <th className="p-3 font-semibold text-slate-500 dark:text-slate-400 w-1/4">Tiêu chí</th>
              {data.map((item, idx) => (
                <th key={idx} className="p-3 font-bold text-slate-900 dark:text-white">
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="w-5 h-5 rounded-full bg-emerald-600 text-white flex items-center justify-center text-[10px] font-black">
                      #{item.rank}
                    </span>
                    <span className="line-clamp-1">{item.name}</span>
                  </div>
                  <div className="text-emerald-600 dark:text-emerald-400 font-extrabold text-sm">
                    {formatPrice(item.price)}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
            {allSpecKeys.map((specKey, i) => (
              <tr key={i} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
                <td className="p-3 font-medium text-slate-500 dark:text-slate-400 bg-slate-50/30 dark:bg-slate-900/50">
                  {specKey}
                </td>
                {data.map((item, colIdx) => (
                  <td key={colIdx} className="p-3 text-slate-800 dark:text-slate-200 font-semibold">
                    {item.specs?.[specKey] || "—"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
