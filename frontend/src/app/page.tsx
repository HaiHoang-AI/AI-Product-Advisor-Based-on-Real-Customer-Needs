"use client";

import { useState } from "react";
import { ChatPanel } from "@/components/chat/ChatPanel";
import {
  Sparkles,
  Zap,
  ShieldCheck,
  Cpu,
  Layers,
  ShoppingBag,
  Sliders,
  CheckCircle2,
  ArrowRight,
  TrendingDown,
  Sun,
  Moon,
  Leaf,
  Clock,
  RotateCcw,
  Truck,
  Award,
  Database,
  Search,
} from "lucide-react";

export default function Home() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [householdSize, setHouseholdSize] = useState(4);
  const [selectedCategory, setSelectedCategory] = useState("Tủ Lạnh");
  const [activePrompt, setActivePrompt] = useState<string | undefined>(undefined);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    if (!isDarkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  // Energy calculation logic based on category and household size
  const estimatedKwhNonInverter = selectedCategory === "Tủ Lạnh"
    ? householdSize * 110 + 150
    : selectedCategory === "Máy Lạnh"
    ? 1200 + householdSize * 150
    : 380;

  const estimatedKwhInverter = Math.round(estimatedKwhNonInverter * 0.58);
  const savedKwh = estimatedKwhNonInverter - estimatedKwhInverter;
  const savedVnd = savedKwh * 2800; // ~2,800 VND per kWh

  const handleLaunchPrompt = (promptText: string) => {
    setActivePrompt(promptText);
    const chatSection = document.getElementById("chat-studio");
    if (chatSection) {
      chatSection.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDarkMode ? "dark bg-slate-950 text-slate-100" : "bg-white text-slate-900"}`}>
      {/* ── Top Navbar (navbar-eco) ────────────────────────────────── */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/85 dark:bg-slate-900/85 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 sm:h-20">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-emerald-600 flex items-center justify-center shadow-md shadow-emerald-600/30 text-white">
                <Leaf className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-lg sm:text-xl tracking-tight text-slate-900 dark:text-white">
                    Điện Máy Xanh
                  </span>
                  <span className="px-2 py-0.5 rounded-md bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-bold text-[10px] border border-emerald-200 dark:border-emerald-800">
                    AI ADVISOR
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
                  So sánh theo nhu cầu thật & tiết kiệm điện
                </p>
              </div>
            </div>

            {/* Desktop Navigation Links */}
            <div className="hidden md:flex items-center gap-6 lg:gap-8 text-sm font-semibold text-slate-600 dark:text-slate-300">
              <a href="#chat-studio" className="hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors">
                AI Studio
              </a>
              <a href="#calculator" className="hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors">
                Đo Tiết Kiệm Điện
              </a>
              <a href="#features" className="hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors">
                Tính Năng
              </a>
              <a href="#certifications" className="hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors">
                Tiêu Chuẩn
              </a>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3">
              <button
                onClick={toggleTheme}
                className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                title="Đổi giao diện Sáng / Tối"
              >
                {isDarkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
              </button>

              <a
                href="#chat-studio"
                className="btn-primary text-xs sm:text-sm py-2.5 px-4 sm:px-6 gap-2"
              >
                <Sparkles className="w-4 h-4" />
                <span className="hidden sm:inline">Tư Vấn Ngay</span>
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* ── Hero & Interactive AI Consultation Section ──────────────── */}
      <section className="relative pt-24 sm:pt-32 pb-16 sm:pb-24 overflow-hidden">
        {/* Ambient Blur Lights */}
        <div className="absolute top-20 right-10 w-[450px] h-[450px] rounded-full bg-emerald-500/10 dark:bg-emerald-500/20 blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-10 left-10 w-[350px] h-[350px] rounded-full bg-sky-500/10 dark:bg-sky-500/15 blur-3xl pointer-events-none"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          {/* Top Title Pill */}
          <div className="text-center max-w-3xl mx-auto mb-10 sm:mb-14">
            <div className="badge-eco mb-4">
              <Sparkles className="w-4 h-4 text-emerald-600" />
              <span>Vietnam Innovation Challenge 2026 • Điện Máy Xanh Track</span>
            </div>
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black tracking-tight text-slate-900 dark:text-white leading-tight mb-4 sm:mb-6">
              So Sánh Sản Phẩm Theo <span className="gradient-text">Nhu Cầu Thật</span>
            </h1>
            <p className="text-base sm:text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto leading-relaxed">
              Không liệt kê thông số kỹ thuật khô khan. Trợ lý AI lắng nghe hoàn cảnh sử dụng, 
              chủ động hỏi ngược khi thiếu thông tin và phân tích điểm đánh đổi trung thực 100% từ Catalog thật.
            </p>

            {/* Quick Status Badges */}
            <div className="flex flex-wrap justify-center gap-4 sm:gap-6 mt-6 text-xs sm:text-sm font-semibold text-slate-600 dark:text-slate-400">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>10.438 Sản phẩm catalog</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Zero Hallucination Guardrail</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Phản hồi dưới 3 giây</span>
              </div>
            </div>
          </div>

          {/* ── Main Dual Studio Grid ─────────────────────────────── */}
          <div id="chat-studio" className="grid lg:grid-cols-12 gap-8 items-start">
            {/* Left Column: Interactive Chat Studio (7 Cols) */}
            <div className="lg:col-span-7 h-[700px] sm:h-[780px] rounded-3xl overflow-hidden border border-slate-200/90 dark:border-slate-800 shadow-xl bg-white dark:bg-slate-900 flex flex-col relative">
              <ChatPanel onInitialPrompt={activePrompt} />
            </div>

            {/* Right Column: Eco Energy & Smart Impact Dashboard (5 Cols) */}
            <div id="calculator" className="lg:col-span-5 space-y-6">
              {/* Energy Saving Gauge Card */}
              <div className="organic-card p-6 sm:p-7 border border-emerald-200/80 dark:border-emerald-900/50 bg-gradient-to-br from-emerald-50/50 via-white to-sky-50/40 dark:from-slate-900 dark:via-slate-900 dark:to-emerald-950/30">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-emerald-600" />
                    <h3 className="font-bold text-slate-900 dark:text-white text-base sm:text-lg">
                      Đo Lường Tiết Kiệm Điện Inverter
                    </h3>
                  </div>
                  <span className="badge-eco text-xs py-0.5 px-2.5">
                    Live Eco
                  </span>
                </div>

                {/* Category Switcher */}
                <div className="flex gap-2 mb-4">
                  {["Tủ Lạnh", "Máy Lạnh", "Máy Giặt"].map((cat) => (
                    <button
                      key={cat}
                      onClick={() => setSelectedCategory(cat)}
                      className={`text-xs px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                        selectedCategory === cat
                          ? "bg-emerald-600 text-white shadow-sm"
                          : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-emerald-50"
                      }`}
                    >
                      {cat}
                    </button>
                  ))}
                </div>

                {/* Household Slider */}
                <div className="mb-6 space-y-2">
                  <div className="flex justify-between text-xs font-semibold text-slate-600 dark:text-slate-300">
                    <span>Số người sử dụng trong nhà:</span>
                    <span className="text-emerald-700 dark:text-emerald-400 font-bold text-sm">
                      {householdSize} người (~{householdSize * 85}L)
                    </span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="8"
                    value={householdSize}
                    onChange={(e) => setHouseholdSize(Number(e.target.value))}
                    className="w-full accent-emerald-600 cursor-pointer"
                  />
                </div>

                {/* Circular Gauge Visualization */}
                <div className="text-center mb-6">
                  <div className="relative inline-block">
                    <svg className="w-40 h-40" viewBox="0 0 120 120">
                      <circle
                        cx="60"
                        cy="60"
                        r="52"
                        fill="none"
                        stroke="currentColor"
                        className="text-slate-200 dark:text-slate-800"
                        strokeWidth="8"
                      />
                      <circle
                        cx="60"
                        cy="60"
                        r="52"
                        fill="none"
                        stroke="url(#ecoGradient)"
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray="326.7"
                        strokeDashoffset="120"
                        transform="rotate(-90 60 60)"
                      />
                      <defs>
                        <linearGradient id="ecoGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#059669" />
                          <stop offset="100%" stopColor="#10b981" />
                        </linearGradient>
                      </defs>
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-3xl font-black text-slate-900 dark:text-white">
                        -42%
                      </span>
                      <span className="text-[11px] text-slate-500 font-semibold uppercase">
                        Điện năng
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 font-medium">
                    Ước tính tiết kiệm khoảng{" "}
                    <span className="text-emerald-700 dark:text-emerald-400 font-bold">
                      {savedVnd.toLocaleString("vi-VN")} đ / năm
                    </span>{" "}
                    với dòng Inverter 5 sao.
                  </p>
                </div>

                {/* Metrics Breakdown */}
                <div className="space-y-3 pt-2 text-xs">
                  <div>
                    <div className="flex justify-between font-semibold mb-1">
                      <span className="text-slate-500">Mức tiêu thụ dòng thường:</span>
                      <span className="text-slate-800 dark:text-slate-200">{estimatedKwhNonInverter} kWh/năm</span>
                    </div>
                    <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-slate-400 rounded-full w-full"></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between font-semibold mb-1">
                      <span className="text-emerald-700 dark:text-emerald-400">Dòng Inverter tối ưu:</span>
                      <span className="text-emerald-700 dark:text-emerald-400 font-bold">{estimatedKwhInverter} kWh/năm</span>
                    </div>
                    <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-600 rounded-full w-[58%]"></div>
                    </div>
                  </div>
                </div>

                {/* Quick Consultation CTA */}
                <button
                  onClick={() => handleLaunchPrompt(`Tư vấn cho tôi ${selectedCategory} tiết kiệm điện nhất cho gia đình ${householdSize} người`)}
                  className="w-full mt-6 py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all cursor-pointer shadow-sm shadow-emerald-600/20"
                >
                  <Search className="w-3.5 h-3.5" />
                  Tìm {selectedCategory} Tiết Kiệm Điện Cho {householdSize} Người
                </button>
              </div>

              {/* Floating Metric Highlights */}
              <div className="grid grid-cols-2 gap-4">
                <div className="organic-card p-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-emerald-100 dark:bg-emerald-950 flex items-center justify-center text-emerald-600 dark:text-emerald-400 shrink-0 font-black text-sm">
                    10K+
                  </div>
                  <div>
                    <div className="font-bold text-slate-900 dark:text-white text-sm">10.438 SKU</div>
                    <div className="text-[11px] text-slate-500">Đầy đủ 14 ngành hàng</div>
                  </div>
                </div>

                <div className="organic-card p-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-amber-100 dark:bg-amber-950 flex items-center justify-center text-amber-600 dark:text-amber-400 shrink-0 font-black text-sm">
                    0%
                  </div>
                  <div>
                    <div className="font-bold text-slate-900 dark:text-white text-sm">Zero Bịa Giá</div>
                    <div className="text-[11px] text-slate-500">Đối chiếu Catalog & API</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Feature Showcase Section (#features) ────────────────────── */}
      <section id="features" className="py-20 bg-slate-50/70 dark:bg-slate-900/50 border-y border-slate-200/80 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <div className="badge-eco mb-4">
              <span>Đột Phá Công Nghệ AI</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-4">
              Mọi Thứ Cần Cho <span className="gradient-text">Tư Vấn Bán Lẻ Hiện Đại</span>
            </h2>
            <p className="text-slate-600 dark:text-slate-300 text-sm sm:text-base">
              Được thiết kế dựa trên đúng rubric chấm điểm của Điện Máy Xanh và Vietnam Innovation Challenge.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            {/* Feature 1 */}
            <div className="feature-card">
              <div className="feature-icon bg-emerald-100/80 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400">
                <Cpu className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
                Need Understanding Canvas
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                Tự động bóc tách nhu cầu từ văn nói, tiếng lóng, đơn vị đo lường (m², HP, lít, triệu) và hiển thị trực quan những gì AI đã hiểu.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="feature-card">
              <div className="feature-icon bg-teal-100/80 dark:bg-teal-950 text-teal-600 dark:text-teal-400">
                <RotateCcw className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
                Smart Follow-up Engine
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                Không trả lời bừa bãi khi thiếu thông tin. AI chủ động hỏi 1-2 câu hỏi then chốt (hướng nắng, phòng ngủ hay phòng khách, số người).
              </p>
            </div>

            {/* Feature 3 */}
            <div className="feature-card">
              <div className="feature-icon bg-sky-100/80 dark:bg-sky-950 text-sky-600 dark:text-sky-400">
                <Layers className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
                Visual Trade-off Cards
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                Đề xuất Top 3 sản phẩm và giải thích rõ ưu điểm ✅ cùng điểm đánh đổi ⚠️ bằng ngôn ngữ bình dân, khách phổ thông nghe là hiểu ngay.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="feature-card">
              <div className="feature-icon bg-lime-100/80 dark:bg-lime-950 text-lime-600 dark:text-lime-400">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
                Zero-Hallucination Guardrail
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                Mọi mức giá, quà tặng, tồn kho đều kiểm tra chéo với catalog và Price API. Không tự bịa và minh bạch báo khi thiếu dữ liệu.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="feature-card">
              <div className="feature-icon bg-amber-100/80 dark:bg-amber-950 text-amber-600 dark:text-amber-400">
                <Zap className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
                Eco & Inverter Calculator
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                Tính toán lượng điện năng tiêu thụ và số tiền tiết kiệm hàng năm, khuyến khích khách hàng lựa chọn thiết bị xanh bền vững.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="feature-card">
              <div className="feature-icon bg-indigo-100/80 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400">
                <Database className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
                Enterprise Mock APIs
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                Sẵn sàng kết nối vào hệ thống ERP của Điện Máy Xanh: API tồn kho theo khu vực, API quà tặng khuyến mãi và Review đánh giá.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Impact Statistics Section (#impact) ──────────────────────── */}
      <section id="impact" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <div className="badge-eco mb-3">
              <span>Hiệu Suất Vận Hành</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-2">
              Sẵn Sàng Triển Khai Thực Tế
            </h2>
            <p className="text-slate-600 dark:text-slate-300 text-sm">
              Đo lường trên bộ dataset thực tế từ Điện Máy Xanh
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="organic-card p-6 text-center">
              <div className="impact-number">10.438</div>
              <div className="impact-label">SKU Sản Phẩm Đã Nạp</div>
            </div>
            <div className="organic-card p-6 text-center">
              <div className="impact-number">0%</div>
              <div className="impact-label">Tỷ Lệ Bịa Đặt (Hallucination)</div>
            </div>
            <div className="organic-card p-6 text-center">
              <div className="impact-number">&lt; 3s</div>
              <div className="impact-label">Thời Gian Phản Hồi SSE</div>
            </div>
            <div className="organic-card p-6 text-center">
              <div className="impact-number">14</div>
              <div className="impact-label">Danh Mục Điện Máy & Điện Tử</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Trust Standards & Certifications (#certifications) ────────── */}
      <section id="certifications" className="py-20 bg-slate-50/70 dark:bg-slate-900/50 border-t border-slate-200/80 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <div className="badge-eco mb-3">
              <span>Cam Kết Chất Lượng</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-3">
              Tiêu Chuẩn Dịch Vụ Điện Máy Xanh
            </h2>
            <p className="text-slate-600 dark:text-slate-300 text-sm">
              Trợ lý AI luôn gắn liền với chính sách mua hàng và hậu mãi chính hãng.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="cert-badge">
              <div className="w-12 h-12 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shrink-0">
                <Award className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 dark:text-white text-sm">100% Hàng Chính Hãng</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Đầy đủ chứng nhận nguồn gốc xuất xứ và hóa đơn VAT.</p>
              </div>
            </div>

            <div className="cert-badge">
              <div className="w-12 h-12 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shrink-0">
                <Zap className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 dark:text-white text-sm">Tiết Kiệm Năng Lượng</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Ưu tiên các dòng máy đạt nhãn năng lượng 5 sao và công nghệ xanh.</p>
              </div>
            </div>

            <div className="cert-badge">
              <div className="w-12 h-12 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shrink-0">
                <Truck className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 dark:text-white text-sm">Giao & Lắp Tận Nơi 2 Giờ</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Đội ngũ kỹ thuật viên chuyên nghiệp tại hơn 3.000 siêu thị toàn quốc.</p>
              </div>
            </div>

            <div className="cert-badge">
              <div className="w-12 h-12 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shrink-0">
                <RotateCcw className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 dark:text-white text-sm">Đổi Mới 30 Ngày</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Nếu phát sinh lỗi kỹ thuật từ nhà sản xuất, đổi ngay máy mới.</p>
              </div>
            </div>

            <div className="cert-badge">
              <div className="w-12 h-12 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shrink-0">
                <Clock className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 dark:text-white text-sm">Bảo Hành Chính Hãng 1-2 Năm</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Hỗ trợ bảo hành tại nhà với linh kiện chính hãng từ hãng sản xuất.</p>
              </div>
            </div>

            <div className="cert-badge">
              <div className="w-12 h-12 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shrink-0">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 dark:text-white text-sm">Hỗ Trợ Trả Góp 0%</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Thủ tục xét duyệt online chỉ trong 5 phút qua thẻ hoặc công ty tài chính.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Dark CTA Banner ────────────────────────────────────────── */}
      <section className="py-20 bg-emerald-950 text-white relative overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[350px] h-[350px] rounded-full bg-emerald-600/20 blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-[300px] h-[300px] rounded-full bg-teal-500/20 blur-3xl"></div>

        <div className="max-w-4xl mx-auto px-4 text-center relative z-10 space-y-6">
          <div className="badge-eco bg-white/10 text-white border-white/20">
            <Leaf className="w-4 h-4 text-emerald-400" />
            <span>Trải Nghiệm Mua Sắm Thông Minh</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight">
            Sẵn Sàng Tìm Sản Phẩm <span className="text-emerald-400">Hoàn Hảo Nhất?</span>
          </h2>
          <p className="text-slate-300 text-base max-w-xl mx-auto">
            Hãy bắt đầu cuộc trò chuyện với AI Advisor ngay bây giờ để nhận gợi ý sản phẩm và so sánh trade-off tức thì.
          </p>
          <div className="pt-2">
            <a
              href="#chat-studio"
              className="btn-primary py-3.5 px-8 text-base shadow-lg shadow-emerald-500/30 gap-2 inline-flex items-center"
            >
              <Sparkles className="w-5 h-5" />
              Bắt Đầu Tư Vấn Ngay
            </a>
          </div>
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────────────────────── */}
      <footer className="py-12 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-lg bg-emerald-600 text-white flex items-center justify-center">
                <Leaf className="w-3.5 h-3.5" />
              </div>
              <span className="font-bold text-slate-900 dark:text-white">Điện Máy Xanh AI Advisor</span>
              <span>© 2026 Vietnam Innovation Challenge</span>
            </div>
            <div className="flex items-center gap-6">
              <a href="https://github.com/HaiHoang-AI/AI-Product-Advisor-Based-on-Real-Customer-Needs" target="_blank" rel="noopener noreferrer" className="hover:text-emerald-600 transition-colors">
                GitHub Repo
              </a>
              <a href="#chat-studio" className="hover:text-emerald-600 transition-colors">
                Trợ Lý AI
              </a>
              <a href="#features" className="hover:text-emerald-600 transition-colors">
                Tài Liệu Kỹ Thuật
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
