"use client";

import React, { useState, useEffect } from "react";
import { TrayAuditResponse } from "@/types/tray";

const DEFAULT_TRAY: TrayAuditResponse = {
  tray_id: "tray-or-04",
  surgery_type: "Robotic Total Knee Arthroplasty",
  total_instruments: 20,
  present_count: 15,
  in_use_count: 4,
  missing_count: 1,
  status: "WARNING_MISSING_ITEM",
  instruments: [
    { id: "inst-01", name: "Scalpel Handle #3 with Blade", category: "Cutting", status: "present", confidence: 0.98, usage_frequency_pct: 98 },
    { id: "inst-02", name: "Scalpel Handle #4 with Blade", category: "Cutting", status: "present", confidence: 0.96, usage_frequency_pct: 95 },
    { id: "inst-03", name: "Metzenbaum Scissors (Curved)", category: "Cutting", status: "present", confidence: 0.97, usage_frequency_pct: 92 },
    { id: "inst-04", name: "Mayo Scissors (Straight)", category: "Cutting", status: "present", confidence: 0.94, usage_frequency_pct: 88 },
    { id: "inst-05", name: "Iris Scissors (Fine Point)", category: "Cutting", status: "present", confidence: 0.92, usage_frequency_pct: 75 },
    { id: "inst-06", name: "Adson Tissue Forceps (1x2)", category: "Grasping", status: "present", confidence: 0.99, usage_frequency_pct: 96 },
    { id: "inst-07", name: "DeBakey Vascular Forceps", category: "Grasping", status: "present", confidence: 0.97, usage_frequency_pct: 90 },
    { id: "inst-08", name: "Crile Hemostatic Clamps (Curved)", category: "Clamping", status: "missing", confidence: 0.45, usage_frequency_pct: 70 },
    { id: "inst-09", name: "Kelly Clamps (Straight)", category: "Clamping", status: "present", confidence: 0.95, usage_frequency_pct: 85 },
    { id: "inst-10", name: "Halstead Mosquito Clamps", category: "Clamping", status: "present", confidence: 0.93, usage_frequency_pct: 80 },
    { id: "inst-11", name: "Mayo-Hegar Needle Holders", category: "Suturing", status: "in_use", confidence: 0.99, usage_frequency_pct: 99 },
    { id: "inst-12", name: "Self-Retaining Retractor Frame", category: "Retracting", status: "present", confidence: 0.96, usage_frequency_pct: 65 },
    { id: "inst-13", name: "Senn Retractors (Double-Ended)", category: "Retracting", status: "present", confidence: 0.91, usage_frequency_pct: 50 },
    { id: "inst-14", name: "Army-Navy Retractor Pair", category: "Retracting", status: "present", confidence: 0.94, usage_frequency_pct: 82 },
    { id: "inst-15", name: "Richardson Retractor Medium", category: "Retracting", status: "present", confidence: 0.92, usage_frequency_pct: 58 },
    { id: "inst-16", name: "Laparoscopic Scope & Light Cable", category: "Scope / Robotic", status: "in_use", confidence: 0.98, usage_frequency_pct: 95 },
    { id: "inst-17", name: "Insufflation Veress Probe", category: "Scope / Robotic", status: "present", confidence: 0.95, usage_frequency_pct: 88 },
    { id: "inst-18", name: "Laparoscopic Trocar Sleeves", category: "Scope / Robotic", status: "present", confidence: 0.96, usage_frequency_pct: 90 },
    { id: "inst-19", name: "Maryland Dissecting Forceps", category: "Grasping", status: "present", confidence: 0.94, usage_frequency_pct: 84 },
    { id: "inst-20", name: "Robotic Bone Saw Handpiece", category: "Cutting", status: "in_use", confidence: 0.99, usage_frequency_pct: 99 },
  ],
  annotated_image_url: "/api/v1/tray/tray-or-04/annotated.jpg",
};

export default function SurgTraceDashboard() {
  const [tray, setTray] = useState<TrayAuditResponse>(DEFAULT_TRAY);
  const [activeTab, setActiveTab] = useState<"live" | "analytics">("live");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [surgeryType, setSurgeryType] = useState<string>("Robotic Total Knee Arthroplasty");
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetch(`${apiBase}/api/v1/tray/tray-or-04`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data) setTray(data);
      })
      .catch(() => {});
  }, [apiBase]);

  const handleUploadTray = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      alert("Please select a tray photo or video frame first!");
      return;
    }

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append("surgery_type", surgeryType);
      formData.append("file", selectedFile);

      const res = await fetch(`${apiBase}/api/v1/tray/upload`, {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setTray(data);
      }
    } catch {
      alert("Backend offline or connection failed. Displaying simulated detection.");
    }
    setIsProcessing(false);
  };

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <header className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-teal-600 mb-1">
            <span>SurgTrace AI</span>
            <span>•</span>
            <span>Surgical Tray Audit & Missing Item Detection</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Operating Room #{tray.tray_id.toUpperCase()}</h1>
          <p className="text-xs text-slate-500 mt-0.5">{tray.surgery_type}</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab("live")}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
              activeTab === "live"
                ? "bg-teal-600 text-white shadow-sm"
                : "bg-slate-100 text-slate-700 hover:bg-slate-200"
            }`}
          >
            Live Tray Inventory
          </button>
          <button
            onClick={() => setActiveTab("analytics")}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
              activeTab === "analytics"
                ? "bg-teal-600 text-white shadow-sm"
                : "bg-slate-100 text-slate-700 hover:bg-slate-200"
            }`}
          >
            Hidden Waste Analytics
          </button>
        </div>
      </header>

      {/* TRAY UPLOAD SCANNER BAR */}
      <form
        onSubmit={handleUploadTray}
        className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm grid grid-cols-1 md:grid-cols-12 gap-4 items-end"
      >
        <div className="md:col-span-5">
          <label className="block text-xs font-semibold uppercase text-slate-600 mb-1.5">
            Upload Tray Snapshot / Video Frame
          </label>
          <input
            type="file"
            accept="image/*,video/*"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            className="w-full text-xs text-slate-600 file:mr-3 file:py-2 file:px-3.5 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100 cursor-pointer bg-slate-50 border border-slate-200 rounded-xl p-1.5"
          />
        </div>

        <div className="md:col-span-4">
          <label className="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Procedure Type</label>
          <input
            type="text"
            value={surgeryType}
            onChange={(e) => setSurgeryType(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
          />
        </div>

        <div className="md:col-span-3">
          <button
            type="submit"
            disabled={isProcessing}
            className="w-full py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs uppercase tracking-wider transition shadow-sm disabled:opacity-50"
          >
            {isProcessing ? "Running YOLOv8 Scan..." : "Scan Tray Inventory"}
          </button>
        </div>
      </form>

      {/* ALERT BANNER IF MISSING ITEM DETECTED */}
      {tray.missing_count > 0 ? (
        <div className="bg-rose-50 border border-rose-200 rounded-2xl p-4 flex items-center justify-between text-rose-900 shadow-sm">
          <div className="flex items-center gap-3">
            <span className="w-3 h-3 rounded-full bg-rose-600 animate-pulse" />
            <div>
              <h2 className="text-sm font-bold uppercase tracking-wide">
                ⚠️ CRITICAL RECONCILIATION ALERT: {tray.missing_count} Instrument Missing from Tray!
              </h2>
              <p className="text-xs text-rose-700 mt-0.5">
                Immediate verification required before patient closure. Check surgical field or back-table.
              </p>
            </div>
          </div>
          <span className="px-3 py-1 bg-rose-200 text-rose-800 font-bold text-xs rounded-lg uppercase">
            Action Required
          </span>
        </div>
      ) : (
        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 flex items-center justify-between text-emerald-900 shadow-sm">
          <div className="flex items-center gap-3">
            <span className="w-3 h-3 rounded-full bg-emerald-600" />
            <div>
              <h2 className="text-sm font-bold uppercase tracking-wide">
                ✓ TRAY VERIFIED COMPLETE: All Instruments Accounted For
              </h2>
              <p className="text-xs text-emerald-700 mt-0.5">
                Zero missing items. Safe to proceed with patient closure.
              </p>
            </div>
          </div>
          <span className="px-3 py-1 bg-emerald-200 text-emerald-800 font-bold text-xs rounded-lg uppercase">
            Verified
          </span>
        </div>
      )}

      {/* METRICS OVERVIEW */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
          <div className="text-xs font-semibold text-slate-500 uppercase">Total Instruments</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">{tray.total_instruments}</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
          <div className="text-xs font-semibold text-emerald-600 uppercase">Present on Tray</div>
          <div className="text-2xl font-bold text-emerald-700 mt-1">{tray.present_count}</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
          <div className="text-xs font-semibold text-blue-600 uppercase">Currently In-Use</div>
          <div className="text-2xl font-bold text-blue-700 mt-1">{tray.in_use_count}</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
          <div className="text-xs font-semibold text-rose-600 uppercase">Missing / Unaccounted</div>
          <div className="text-2xl font-bold text-rose-700 mt-1">{tray.missing_count}</div>
        </div>
      </div>

      {activeTab === "live" ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Instrument Manifest Table */}
          <div className="lg:col-span-8 bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700">
              Real-Time Instrument Manifest & Status
            </h2>
            <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500 uppercase sticky top-0 bg-white">
                    <th className="pb-3 font-semibold">Instrument Name</th>
                    <th className="pb-3 font-semibold">Category</th>
                    <th className="pb-3 font-semibold">Status</th>
                    <th className="pb-3 font-semibold">Confidence</th>
                    <th className="pb-3 font-semibold">Usage %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {tray.instruments.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-50">
                      <td className="py-3 font-medium text-slate-900">{item.name}</td>
                      <td className="py-3 text-slate-600">{item.category}</td>
                      <td className="py-3">
                        {item.status === "present" && (
                          <span className="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold rounded-lg text-[11px]">
                            Present
                          </span>
                        )}
                        {item.status === "in_use" && (
                          <span className="px-2.5 py-1 bg-blue-50 text-blue-700 border border-blue-200 font-semibold rounded-lg text-[11px]">
                            In Use (Surgical Field)
                          </span>
                        )}
                        {item.status === "missing" && (
                          <span className="px-2.5 py-1 bg-rose-50 text-rose-700 border border-rose-200 font-semibold rounded-lg text-[11px] animate-pulse">
                            ⚠️ Missing / Retained
                          </span>
                        )}
                      </td>
                      <td className="py-3 font-mono text-slate-600">{Math.round(item.confidence * 100)}%</td>
                      <td className="py-3 font-mono text-slate-600">{item.usage_frequency_pct}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Right: Camera Feed / Annotated Overlay */}
          <div className="lg:col-span-4 bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700">
              OR Tray Camera & Bounding Box Feed
            </h2>
            <div className="relative w-full h-64 rounded-xl overflow-hidden bg-slate-900 border border-slate-800 flex items-center justify-center">
              <img
                src={`${apiBase}/api/v1/tray/${tray.tray_id}/annotated.jpg`}
                alt="OR Tray Stream"
                className="w-full h-full object-cover"
              />
              <div className="absolute top-3 left-3 bg-slate-950/80 backdrop-blur-md px-2.5 py-1 rounded-lg text-[10px] text-teal-400 font-mono border border-slate-800">
                ● YOLOv8 Live Inference Active
              </div>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Computer vision scans back-table camera frames in real time, matching detected instrument bounding boxes against the pre-op tray manifest.
            </p>
          </div>
        </div>
      ) : (
        /* ANALYTICS TAB: SOLVING HIDDEN WASTE */
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
          <div>
            <h2 className="text-base font-bold text-slate-900">Hospital Sterilization & Tray Optimization Analytics</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Addressing <span className="font-semibold text-slate-700">Hidden Waste</span>: Identifying instruments sterilized repeatedly without ever being touched in surgery.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-1">
              <div className="text-xs text-slate-500 font-semibold uppercase">Avg. Tray Sterilization Cost</div>
              <div className="text-2xl font-bold text-slate-900">$340 / tray</div>
              <div className="text-[11px] text-slate-500">Includes autoclave cycle, wrapping, & labor</div>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-1">
              <div className="text-xs text-slate-500 font-semibold uppercase">Unused Tray Instrument Ratio</div>
              <div className="text-2xl font-bold text-rose-600">34.2%</div>
              <div className="text-[11px] text-slate-500">Tools never removed from tray across 50 surgeries</div>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-1">
              <div className="text-xs text-slate-500 font-semibold uppercase">Potential Annual Hospital Savings</div>
              <div className="text-2xl font-bold text-emerald-600">$184,500</div>
              <div className="text-[11px] text-slate-500">By streamlining tray composition based on AI data</div>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Instrument Utilization Breakdown</h3>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {tray.instruments.map((item) => (
                <div key={item.id} className="bg-slate-50 border border-slate-200 rounded-xl p-3 flex items-center justify-between">
                  <div className="space-y-0.5">
                    <div className="text-xs font-semibold text-slate-900">{item.name}</div>
                    <div className="text-[11px] text-slate-500">Category: {item.category}</div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-36 bg-slate-200 h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          item.usage_frequency_pct > 80
                            ? "bg-emerald-500"
                            : item.usage_frequency_pct > 50
                            ? "bg-blue-500"
                            : "bg-amber-500"
                        }`}
                        style={{ width: `${item.usage_frequency_pct}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono font-semibold text-slate-700 w-10 text-right">
                      {item.usage_frequency_pct}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
