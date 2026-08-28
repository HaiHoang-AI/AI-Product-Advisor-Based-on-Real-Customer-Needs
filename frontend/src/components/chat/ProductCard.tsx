import { Product } from "./types";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function ProductCard({ product, rank }: { product: Product; rank?: number }) {
  const formatPrice = (price: number) => new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(price);

  const rankColor = rank === 1 ? "bg-green-500" : rank === 2 ? "bg-slate-400" : rank === 3 ? "bg-amber-600" : "bg-gray-200 text-gray-800";

  return (
    <Card className="my-2 border-green-100 shadow-sm">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg font-bold text-gray-900">{product.name}</CardTitle>
            <p className="text-sm text-gray-500">{product.brand}</p>
          </div>
          {rank && <Badge className={`${rankColor} text-white`}>#{rank}</Badge>}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-col">
          {product.promo_price ? (
            <>
              <span className="text-lg font-bold text-red-600">{formatPrice(product.promo_price)}</span>
              <span className="text-sm text-gray-500 line-through">{formatPrice(product.price)}</span>
            </>
          ) : (
            <span className="text-lg font-bold text-red-600">{formatPrice(product.price)}</span>
          )}
        </div>

        {product.gifts && product.gifts.length > 0 && (
          <div className="bg-red-50 p-2 rounded-md border border-red-100">
            <p className="text-xs font-semibold text-red-800 mb-1">🎁 Quà tặng khuyến mãi:</p>
            <ul className="text-xs text-red-700 list-disc pl-4 space-y-1">
              {product.gifts.map((gift, i) => (
                <li key={i}>{gift}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="space-y-2">
          {product.strengths?.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-green-700">✅ Ưu điểm:</p>
              <ul className="text-sm list-disc pl-5 space-y-1 text-gray-700">
                {product.strengths.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}
          {product.trade_offs?.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-amber-600">⚠️ Đánh đổi:</p>
              <ul className="text-sm list-disc pl-5 space-y-1 text-gray-700">
                {product.trade_offs.map((t, i) => (
                  <li key={i}>{t}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </CardContent>
      <CardFooter className="pt-0">
        <p className="text-sm font-medium text-gray-800 italic bg-gray-50 p-2 rounded-md w-full">{product.summary}</p>
      </CardFooter>
    </Card>
  );
}
