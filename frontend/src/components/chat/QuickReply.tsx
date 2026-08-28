"use client";

import { MessageSquarePlus } from "lucide-react";

export function QuickReply({
  replies,
  onSelect,
}: {
  replies: string[];
  onSelect: (reply: string) => void;
}) {
  if (!replies || replies.length === 0) return null;

  return (
    <div className="my-2 space-y-1.5">
      <div className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-800 dark:text-emerald-300 uppercase tracking-wider pl-1">
        <MessageSquarePlus className="w-3.5 h-3.5 text-emerald-600" />
        Gợi ý câu trả lời nhanh:
      </div>
      <div className="flex flex-wrap gap-2">
        {replies.map((reply, i) => (
          <button
            key={i}
            onClick={() => onSelect(reply)}
            className="px-3.5 py-1.5 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-200 border border-emerald-200/80 dark:border-emerald-800/80 hover:bg-emerald-600 hover:text-white hover:border-emerald-600 dark:hover:bg-emerald-500 dark:hover:text-slate-950 transition-all duration-200 shadow-xs active:scale-95 cursor-pointer"
          >
            {reply}
          </button>
        ))}
      </div>
    </div>
  );
}
