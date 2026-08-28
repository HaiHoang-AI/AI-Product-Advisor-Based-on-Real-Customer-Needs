import { NeedSummaryData } from "./types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, HelpCircle } from "lucide-react";

export function NeedSummary({ data }: { data: NeedSummaryData }) {
  const renderValue = (val: string | string[] | undefined) => {
    if (!val || (Array.isArray(val) && val.length === 0)) {
      return (
        <span className="flex items-center text-amber-600 text-sm italic">
          <HelpCircle className="w-3 h-3 mr-1" />
          Chưa rõ
        </span>
      );
    }
    if (Array.isArray(val)) {
      return (
        <div className="flex flex-wrap gap-1">
          {val.map((v, i) => (
            <Badge key={i} variant="outline" className="bg-green-50 text-green-700 border-green-200">
              {v}
            </Badge>
          ))}
        </div>
      );
    }
    return <span className="text-sm font-medium text-gray-800">{val}</span>;
  };

  return (
    <Card className="my-2 border-blue-100 bg-blue-50/50 shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-bold text-blue-900 flex items-center">
          <CheckCircle2 className="w-4 h-4 mr-2 text-blue-600" />
          Thông tin nhu cầu AI đã hiểu
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="text-gray-500">Loại sản phẩm:</div>
          <div>{renderValue(data.category)}</div>
          
          <div className="text-gray-500">Mức giá:</div>
          <div>{renderValue(data.budget)}</div>
          
          <div className="text-gray-500">Số người dùng:</div>
          <div>{renderValue(data.household_size)}</div>
          
          <div className="text-gray-500">Ưu tiên chính:</div>
          <div>{renderValue(data.priorities)}</div>
          
          <div className="text-gray-500">Diện tích phòng:</div>
          <div>{renderValue(data.room_area)}</div>
        </div>
      </CardContent>
    </Card>
  );
}
