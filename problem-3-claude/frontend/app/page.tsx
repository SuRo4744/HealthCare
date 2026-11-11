export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900">
      <div className="max-w-7xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300 text-sm font-medium mb-6">
            <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse" />
            Video to 3D Model to Explainer Video
          </div>
          <h1 className="text-5xl font-bold tracking-tight text-slate-900 dark:text-white mb-6">
            Healthcare Product Visualization
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-3xl mx-auto">
            Turn simple phone videos into 3D models and explainer videos.
            No CAD experts needed. No expensive scanners.
          </p>
        </div>

        {/* Pain Points */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <div className="text-3xl mb-3">📸</div>
            <h3 className="font-semibold text-slate-900 dark:text-white mb-2">Flat & Heavy</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Photos and physical demo kits don't show products clearly
            </p>
          </div>
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <div className="text-3xl mb-3">⏱️</div>
            <h3 className="font-semibold text-slate-900 dark:text-white mb-2">Slow to Produce</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Training videos take weeks and outside agencies
            </p>
          </div>
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <div className="text-3xl mb-3">💰</div>
            <h3 className="font-semibold text-slate-900 dark:text-white mb-2">Expensive to Change</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              New finish, language, or audience means starting over
            </p>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <a
            href="/upload"
            className="inline-flex items-center gap-2 px-8 py-4 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-full font-semibold hover:opacity-90 transition-opacity"
          >
            Start New Project
          </a>
          <p className="mt-4 text-sm text-slate-500 dark:text-slate-500">
            Upload videos or photos → Auto 3D reconstruction → Explainer video
          </p>
        </div>
      </div>
    </main>
  );
}
