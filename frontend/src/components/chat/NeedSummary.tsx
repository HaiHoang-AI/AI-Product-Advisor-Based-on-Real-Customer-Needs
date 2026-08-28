"use client";

import { NeedSummaryData } from "./types";
import { Sparkles, Check, HelpCircle, UserCheck, DollarSign, Home, Sliders } from "lucide-react";

export function NeedSummary({ data }: { data: NeedSummaryData }) {
  const items = [
    { label: "Ngành hàng", value: data.category, icon: Home },
    { label: "Ngân sách", value: data.budget || data.budget_min, icon: DollarSign },
    { label: "Quy mô sử dụng", value: data.household_size, icon: UserCheck },
    { label: "Không gian phòng", value: data.room_area || data.room_type, icon: Home },
    { label: "Ưu tiên chính", value: data.priorities, icon: Sliders },
    { label: "Mục đích sử dụng", value: data.usage_purpose, icon: Sparkles },
  ];

  return (
    <div className="organic-card overflow-hidden my-3 border border-emerald-200/80 bg-gradient-to-br from-emerald-50/70 via-white to-teal-50/50 dark:from-emerald-950/40 dark:via-slate-900 dark:to-teal-950/30 shadow-sm">
      {/* Header */}
      <div className="p-3.5 sm:p-4 border-b border-emerald-100 dark:border-emerald-900/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-sm shadow-emerald-500/30">
            <Sparkles className="w-4 h-4" />
          </div>
          <h4 className="text-xs sm:text-sm font-bold text-emerald-950 dark:text-emerald-200 uppercase tracking-wider">
            Need Understanding Canvas — AI đã phân tích nhu cầu
          </h4>
        </div>
        <span className="badge-eco text-[11px] py-0.5 px-2.5">
          ✓ Tự động cập nhật
        </span>
      </div>

      {/* Grid of Identified Needs */}
      <div className="p-4 grid grid-cols-2 sm:grid-cols-3 gap-2.5 sm:gap-3 text-xs">
        {items.map((item, idx) => {
          const Icon = item.icon;
          const hasVal = Boolean(item.value && (Array.isArray(item.value) ? item.value.length > 0 : true));

          return (
            <div
              key={idx}
              className={`p-2.5 rounded-xl border transition-all ${
                hasVal
                  ? "bg-white dark:bg-slate-800/80 border-emerald-100 dark:border-emerald-900/40 shadow-xs"
                  : "bg-slate-50/60 dark:bg-slate-900/40 border-slate-200/60 dark:border-slate-800"
              }`}
            >
              <div className="flex items-center gap-1.5 text-slate-400 dark:text-slate-500 mb-1 font-medium text-[11px]">
                <Icon className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                {item.label}
              </div>
              <div>
                {hasVal ? (
                  Array.isArray(item.value) ? (
                    <div className="flex flex-wrap gap-1 mt-0.5">
                      {item.value.map((v, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded-md bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-semibold text-[11px] border border-emerald-200/60 dark:border-emerald-800/60"
                        >
                          {v}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span className="font-bold text-slate-900 dark:text-white capitalize">
                      {String(item.value)}
                    </span>
                  )
                ) : (
                  <span className="inline-flex items-center gap-1 text-slate-400 dark:text-slate-500 italic text-[11px]">
                    <HelpCircle className="w-3 h-3 text-slate-400" />
                    Chưa xác định
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
