import React from 'react'
import './index.css'

// Simple test component to verify enhanced UI is working
function TestApp() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute top-3/4 right-1/4 w-72 h-72 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
      </div>

      {/* Header */}
      <header className="relative bg-white/80 backdrop-blur-lg shadow-lg border-b border-gray-200/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                    <span className="text-white font-bold">⚡</span>
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white animate-pulse"></div>
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Lane MCP Enhanced
                  </h1>
                  <p className="text-sm text-gray-500">AI-Powered Campaign Management</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white/70 backdrop-blur-lg rounded-2xl p-8 shadow-xl border-0 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white rounded-xl mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                <span className="text-2xl">✨</span>
              </div>
              <div>
                <h2 className="text-xl text-white font-bold">Enhanced UI Test</h2>
                <p className="text-blue-100">If you can see gradients and blur effects, the enhanced UI is working!</p>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-gradient-to-r from-emerald-50 to-blue-50 rounded-lg border border-emerald-200">
              <h3 className="font-semibold text-emerald-800">✅ Enhanced UI is Active!</h3>
              <p className="text-emerald-600">You should see beautiful gradients, blur effects, and animations.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-white/70 backdrop-blur-lg rounded-xl shadow-lg border-0 hover:shadow-xl hover:scale-105 transition-all duration-300">
                <h4 className="font-semibold text-gray-800">Glass Morphism</h4>
                <p className="text-gray-600 text-sm">Backdrop blur effects</p>
              </div>
              <div className="p-4 bg-white/70 backdrop-blur-lg rounded-xl shadow-lg border-0 hover:shadow-xl hover:scale-105 transition-all duration-300">
                <h4 className="font-semibold text-gray-800">Hover Animation</h4>
                <p className="text-gray-600 text-sm">Smooth scale effect</p>
              </div>
              <div className="p-4 bg-white/70 backdrop-blur-lg rounded-xl shadow-lg border-0 hover:shadow-xl hover:scale-105 transition-all duration-300">
                <h4 className="font-semibold text-gray-800">Modern Design</h4>
                <p className="text-gray-600 text-sm">Professional styling</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default TestApp
