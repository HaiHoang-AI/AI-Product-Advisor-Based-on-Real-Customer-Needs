import { ChatPanel } from "@/components/chat/ChatPanel";
import { MonitorSmartphone, ShoppingCart, Zap } from "lucide-react";

export default function Home() {
  return (
    <main className="flex h-screen w-full bg-slate-50 overflow-hidden">
      {/* Sidebar - Desktop Only */}
      <div className="hidden md:flex w-80 bg-[#00a651] text-white flex-col">
        <div className="p-6 border-b border-green-600">
          <h1 className="text-2xl font-bold tracking-tight">Điện Máy Xanh</h1>
          <p className="text-green-100 text-sm mt-1">Trợ lý AI tư vấn sản phẩm</p>
        </div>
        
        <div className="flex-1 p-6 space-y-6">
          <div>
            <h2 className="text-sm font-semibold text-green-200 uppercase tracking-wider mb-4">Tính năng</h2>
            <ul className="space-y-4">
              <li className="flex items-start gap-3">
                <MonitorSmartphone className="w-5 h-5 text-green-200 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-white">Tư vấn thông minh</p>
                  <p className="text-sm text-green-100 mt-1">Gợi ý sản phẩm phù hợp với nhu cầu thực tế</p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <Zap className="w-5 h-5 text-green-200 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-white">So sánh trực quan</p>
                  <p className="text-sm text-green-100 mt-1">Phân tích ưu/nhược điểm các lựa chọn tốt nhất</p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <ShoppingCart className="w-5 h-5 text-green-200 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-white">Mua sắm dễ dàng</p>
                  <p className="text-sm text-green-100 mt-1">Thông tin cập nhật mới nhất từ cửa hàng</p>
                </div>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="p-6 border-t border-green-600 text-xs text-green-200">
          © 2026 Điện Máy Xanh AI Advisor
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full bg-white relative shadow-2xl z-10 md:rounded-l-2xl border-l border-slate-200 overflow-hidden">
        {/* Mobile Header */}
        <div className="md:hidden flex items-center p-4 bg-[#00a651] text-white">
          <h1 className="font-bold">Trợ lý AI Điện Máy Xanh</h1>
        </div>
        
        <div className="flex-1 overflow-hidden">
          <ChatPanel />
        </div>
      </div>
    </main>
  );
}
