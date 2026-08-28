import { Comparison } from "./types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function ComparisonView({ data }: { data: Comparison }) {
  if (!data || !data.products || data.products.length === 0) return null;

  return (
    <Card className="my-2 border-slate-200 bg-white shadow-sm overflow-hidden">
      <CardHeader className="bg-slate-50 border-b border-slate-100 pb-3">
        <CardTitle className="text-md font-bold text-slate-800">Bảng So Sánh</CardTitle>
      </CardHeader>
      <CardContent className="p-0 overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-3 border-b font-medium">Đặc điểm</th>
              {data.products.map((p, i) => (
                <th key={p.id} className="px-4 py-3 border-b border-l font-medium min-w-[150px]">
                  <div className="flex flex-col gap-1">
                    <Badge variant="outline" className="w-fit text-xs mb-1">
                      Lựa chọn {i + 1}
                    </Badge>
                    <span className="font-bold text-gray-900 line-clamp-2">{p.name}</span>
                    <span className="text-red-600 font-semibold mt-1">
                      {new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(p.promo_price || p.price)}
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.entries(data.differences || {}).map(([feature, values], i) => (
              <tr key={feature} className={i % 2 === 0 ? "bg-white" : "bg-slate-50/50"}>
                <td className="px-4 py-3 border-b font-medium text-slate-700">{feature}</td>
                {/* Assuming differences are structured appropriately. For now, just rendering standard fields if custom diffs are complex */}
                {data.products.map((p) => (
                  <td key={p.id} className="px-4 py-3 border-b border-l text-slate-600">
                    {/* Render actual values here, simplified for example */}
                    {p.strengths.includes(feature) ? <span className="text-green-600">✅ Có</span> : "-"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        
        {/* Simple stacked view for mobile if needed, though overflow-x-auto handles tables okay */}
      </CardContent>
    </Card>
  );
}
