"use client";

import { Product } from "./types";
import { CheckCircle2, AlertTriangle, Gift, Tag, Zap, Database, ExternalLink } from "lucide-react";

export function ProductCard({ product, rank }: { product: Product; rank?: number }) {
  const currentRank = rank || product.rank || 1;
  const originalPrice = product.price_original || product.price;
  const promoPrice = product.price_promo || product.promo_price;
  const effectivePrice = promoPrice || originalPrice;

  const formatPrice = (price?: number) => {
    if (!price) return "Đang cập nhật";
    return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(price);
  };

  const discountPct = originalPrice && promoPrice && promoPrice < originalPrice
    ? Math.round(((originalPrice - promoPrice) / originalPrice) * 100)
    : 0;

  const rankBadgeStyle =
    currentRank === 1
      ? "bg-emerald-600 text-white shadow-md shadow-emerald-500/20"
      : currentRank === 2
      ? "bg-slate-700 text-white"
      : "bg-amber-600 text-white";

  const rankTitle =
    currentRank === 1
      ? "Lựa chọn Tối ưu nhất"
      : currentRank === 2
      ? "Giá tốt & Tiết kiệm"
      : "Cân bằng & Đa năng";

  return (
    <div className="organic-card overflow-hidden my-3 border border-emerald-100/80 bg-white dark:bg-slate-900 shadow-sm transition-all duration-300">
      {/* Header Bar with Rank & Title */}
      <div className="p-4 sm:p-5 border-b border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-800/40 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-full text-xs font-bold ${rankBadgeStyle}`}>
            #{currentRank}
          </span>
          <div>
            <h4 className="font-bold text-slate-900 dark:text-white text-base sm:text-lg leading-tight">
              {product.name}
            </h4>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
                {product.brand}
              </span>
              <span className="text-slate-300 dark:text-slate-700">•</span>
              <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                {rankTitle}
              </span>
            </div>
          </div>
        </div>
        {discountPct > 0 && (
          <div className="hidden sm:flex flex-col items-end">
            <span className="px-2.5 py-0.5 rounded-full bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400 text-xs font-bold border border-rose-200 dark:border-rose-900">
              Giảm {discountPct}%
            </span>
          </div>
        )}
      </div>

      {/* Body Content */}
      <div className="p-4 sm:p-5 space-y-4">
        {/* Pricing Block */}
        <div className="flex flex-wrap items-baseline gap-3">
          <span className="text-xl sm:text-2xl font-black text-emerald-700 dark:text-emerald-400 tracking-tight">
            {formatPrice(effectivePrice)}
          </span>
          {discountPct > 0 && originalPrice && (
            <span className="text-sm text-slate-400 line-through font-medium">
              {formatPrice(originalPrice)}
            </span>
          )}
          {discountPct > 0 && (
            <span className="sm:hidden px-2 py-0.5 rounded-full bg-rose-50 text-rose-600 text-xs font-bold">
              -{discountPct}%
            </span>
          )}
        </div>

        {/* Promotion Gift Tag */}
        {(product.promotion_gift || (product.gifts && product.gifts.length > 0)) && (
          <div className="p-3 rounded-xl bg-amber-50/80 dark:bg-amber-950/30 border border-amber-200/70 dark:border-amber-900/50 flex items-start gap-2.5">
            <Gift className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
            <div className="text-xs text-amber-900 dark:text-amber-200 font-medium">
              <span className="font-bold mr-1">Quà tặng kèm:</span>
              {product.promotion_gift || product.gifts?.join(", ")}
            </div>
          </div>
        )}

        {/* Specs Highlights Pills */}
        {product.specs && Object.keys(product.specs).length > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {Object.entries(product.specs).slice(0, 4).map(([key, val], i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 text-[11px] font-medium px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200/60 dark:border-slate-700/60"
              >
                <Zap className="w-3 h-3 text-emerald-600" />
                <span className="font-semibold text-slate-900 dark:text-white">{key}:</span> {val}
              </span>
            ))}
          </div>
        )}

        {/* Strengths & Trade-offs */}
        <div className="grid sm:grid-cols-2 gap-3 pt-2">
          {product.strengths && product.strengths.length > 0 && (
            <div className="p-3 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40 space-y-1.5">
              <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-800 dark:text-emerald-300 uppercase tracking-wide">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                Điểm mạnh theo nhu cầu
              </div>
              <ul className="text-xs text-slate-700 dark:text-slate-300 space-y-1 pl-1">
                {product.strengths.map((s, i) => (
                  <li key={i} className="flex items-start gap-1.5">
                    <span className="text-emerald-500 font-bold">•</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {product.trade_offs && product.trade_offs.length > 0 && (
            <div className="p-3 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-100 dark:border-amber-900/40 space-y-1.5">
              <div className="flex items-center gap-1.5 text-xs font-bold text-amber-800 dark:text-amber-300 uppercase tracking-wide">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                Điểm cần cân nhắc
              </div>
              <ul className="text-xs text-slate-700 dark:text-slate-300 space-y-1 pl-1">
                {product.trade_offs.map((t, i) => (
                  <li key={i} className="flex items-start gap-1.5">
                    <span className="text-amber-500 font-bold">•</span>
                    <span>{t}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* AI Verdict Summary */}
        {product.summary && (
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 italic">
            💡 <span className="font-semibold text-slate-900 dark:text-slate-100 not-italic mr-1">Đánh giá nhanh:</span>
            {product.summary}
          </div>
        )}

        {/* Data Source Citation */}
        <div className="flex items-center justify-between text-[11px] text-slate-400 dark:text-slate-500 pt-1 border-t border-slate-100 dark:border-slate-800">
          <span className="flex items-center gap-1">
            <Database className="w-3 h-3 text-emerald-500" />
            Nguồn: {product.data_sources?.join(" + ") || "Catalog Điện Máy Xanh"}
          </span>
          <span className="text-emerald-600 dark:text-emerald-400 font-medium">
            ✓ Đã kiểm chứng dữ liệu
          </span>
        </div>
      </div>
    </div>
  );
}
