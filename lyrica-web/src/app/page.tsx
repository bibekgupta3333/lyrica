import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="max-w-4xl w-full space-y-8 text-center">
        {/* Header */}
        <div className="space-y-4">
          <h1 className="text-6xl font-bold text-gray-900">
            🎵 Lyrica
          </h1>
          <p className="text-2xl text-gray-600">
            Agentic Song Lyrics Generator
          </p>
          <p className="text-lg text-gray-500 max-w-2xl mx-auto">
            Generate creative song lyrics using AI agents powered by RAG and local LLMs
          </p>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <StatusCard 
            title="Backend API"
            status="running"
            url="http://localhost:8000"
          />
          <StatusCard 
            title="API Docs"
            status="ready"
            url="http://localhost:8000/docs"
          />
          <StatusCard 
            title="Health Check"
            status="healthy"
            url="http://localhost:8000/api/v1/health/health"
          />
        </div>

        {/* Features */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
          <FeatureCard 
            icon="🤖"
            title="AI Agents"
            description="Multi-agent system using LangGraph for intelligent lyrics generation"
          />
          <FeatureCard 
            icon="🔍"
            title="RAG System"
            description="Retrieval Augmented Generation with ChromaDB vector store"
          />
          <FeatureCard 
            icon="💻"
            title="Local LLM"
            description="Powered by Ollama with Llama 3 / Mistral models"
          />
          <FeatureCard 
            icon="⚡"
            title="Real-time"
            description="WebSocket streaming for live lyrics generation"
          />
        </div>

        {/* CTA */}
        <div className="mt-12 flex gap-4 justify-center">
          <Link 
            href="http://localhost:8000/docs"
            target="_blank"
            className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            View API Docs
          </Link>
          <Link 
            href="/generate"
            className="px-8 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition"
          >
            Generate Lyrics
          </Link>
        </div>

        {/* Tech Stack */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500 mb-4">Built with</p>
          <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-600">
            <span className="px-3 py-1 bg-white rounded-full border">FastAPI</span>
            <span className="px-3 py-1 bg-white rounded-full border">Next.js</span>
            <span className="px-3 py-1 bg-white rounded-full border">React Native</span>
            <span className="px-3 py-1 bg-white rounded-full border">LangGraph</span>
            <span className="px-3 py-1 bg-white rounded-full border">ChromaDB</span>
            <span className="px-3 py-1 bg-white rounded-full border">PostgreSQL</span>
            <span className="px-3 py-1 bg-white rounded-full border">TurboRepo</span>
          </div>
        </div>
      </div>
    </main>
  );
}

function StatusCard({ title, status, url }: { title: string; status: string; url: string }) {
  return (
    <a 
      href={url}
      target="_blank"
      className="p-6 bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition"
    >
      <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        <span className="text-sm text-gray-600">{status}</span>
      </div>
    </a>
  );
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="p-6 bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}
