import React, { useState } from 'react';
import { Code, Zap, Shield, PlayCircle, Key, Mail, FileText, Eye, ArrowRight, Check, Github, Twitter } from 'lucide-react';

export default function CrawlicLanding() {
  const [activeTab, setActiveTab] = useState('page-content');
  const [apiKey, setApiKey] = useState('');
  const [testUrl, setTestUrl] = useState('https://example.com');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');

  const endpoints = [
    { id: 'page-content', name: 'Page Content', icon: FileText, description: 'Extract raw HTML' },
    { id: 'describe-page', name: 'AI Analysis', icon: Eye, description: 'Get AI summary' },
    { id: 'find-contact-email', name: 'Find Emails', icon: Mail, description: 'Extract emails' }
  ];

  const handleTest = async () => {
    if (!apiKey) {
      alert('Please enter your API key first');
      return;
    }
    
    setLoading(true);
    setResult(null);
    
    try {
      const response = await fetch(`https://crawlic.ialae.com/api/${activeTab}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({ link: testUrl })
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleGetApiKey = async () => {
    if (!email || !name) {
      alert('Please enter your name and email');
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch('https://crawlic.ialae.com/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email })
      });
      
      const data = await response.json();
      if (data.api_key) {
        setApiKey(data.api_key);
        alert('API Key generated! It has been filled in the test section.');
      }
    } catch (error) {
      alert('Error generating API key: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Navigation */}
      <nav className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Code className="w-8 h-8 text-blue-400" />
            <span className="text-2xl font-bold">Crawlic</span>
          </div>
          <div className="flex items-center gap-6">
            <a href="#features" className="hover:text-blue-400 transition">Features</a>
            <a href="#playground" className="hover:text-blue-400 transition">Playground</a>
            <a href="#pricing" className="hover:text-blue-400 transition">Pricing</a>
            <a href="https://crawlic.ialae.com/api/api/docs" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition">
              API Docs
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="inline-block mb-4 px-4 py-2 bg-blue-500/20 border border-blue-500/30 rounded-full text-blue-300 text-sm">
          ✨ Intelligent Web Scraping API
        </div>
        <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
          Extract Web Data
          <br />with AI Power
        </h1>
        <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
          Simple REST API for web scraping, content extraction, and AI-powered analysis. 
          No complex setup, just clean JSON responses.
        </p>
        <div className="flex gap-4 justify-center">
          <a href="#playground" className="px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold flex items-center gap-2 transition transform hover:scale-105">
            Try Live Demo <ArrowRight className="w-5 h-5" />
          </a>
          <a href="#get-key" className="px-8 py-4 bg-slate-700 hover:bg-slate-600 rounded-lg font-semibold transition">
            Get API Key
          </a>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="max-w-7xl mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center mb-12">Why Crawlic?</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 hover:border-blue-500/50 transition">
            <Zap className="w-12 h-12 text-blue-400 mb-4" />
            <h3 className="text-2xl font-bold mb-3">Lightning Fast</h3>
            <p className="text-slate-300">Built on SeleniumBase for reliable, JavaScript-rendered content extraction</p>
          </div>
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 hover:border-purple-500/50 transition">
            <Eye className="w-12 h-12 text-purple-400 mb-4" />
            <h3 className="text-2xl font-bold mb-3">AI-Powered</h3>
            <p className="text-slate-300">Get intelligent summaries and page classification using advanced AI</p>
          </div>
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 hover:border-pink-500/50 transition">
            <Shield className="w-12 h-12 text-pink-400 mb-4" />
            <h3 className="text-2xl font-bold mb-3">Secure & Reliable</h3>
            <p className="text-slate-300">API key authentication, rate limiting, and 99.9% uptime guarantee</p>
          </div>
        </div>
      </section>

      {/* Get API Key Section */}
      <section id="get-key" className="max-w-3xl mx-auto px-4 py-20">
        <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-8">
          <div className="text-center mb-8">
            <Key className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-2">Get Your API Key</h2>
            <p className="text-slate-300">Free tier includes 1,000 requests per month</p>
          </div>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Your Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 bg-slate-900 border border-slate-600 rounded-lg focus:border-blue-500 focus:outline-none"
            />
            <input
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 bg-slate-900 border border-slate-600 rounded-lg focus:border-blue-500 focus:outline-none"
            />
            <button
              onClick={handleGetApiKey}
              disabled={loading}
              className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold disabled:opacity-50 transition"
            >
              {loading ? 'Generating...' : 'Generate API Key'}
            </button>
          </div>
        </div>
      </section>

      {/* Interactive Playground */}
      <section id="playground" className="max-w-7xl mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center mb-4">Interactive Playground</h2>
        <p className="text-center text-slate-300 mb-12">Test all endpoints right here in your browser</p>
        
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left: Input Section */}
          <div className="space-y-6">
            {/* API Key Input */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <label className="block text-sm font-semibold mb-2 text-slate-300">API Key</label>
              <input
                type="text"
                placeholder="Bearer your_api_key_here"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full px-4 py-3 bg-slate-900 border border-slate-600 rounded-lg focus:border-blue-500 focus:outline-none font-mono text-sm"
              />
            </div>

            {/* Endpoint Selection */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <label className="block text-sm font-semibold mb-3 text-slate-300">Select Endpoint</label>
              <div className="space-y-2">
                {endpoints.map(endpoint => (
                  <button
                    key={endpoint.id}
                    onClick={() => setActiveTab(endpoint.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                      activeTab === endpoint.id
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-900 hover:bg-slate-700 text-slate-300'
                    }`}
                  >
                    <endpoint.icon className="w-5 h-5" />
                    <div className="text-left flex-1">
                      <div className="font-semibold">{endpoint.name}</div>
                      <div className="text-xs opacity-70">{endpoint.description}</div>
                    </div>
                    {activeTab === endpoint.id && <Check className="w-5 h-5" />}
                  </button>
                ))}
              </div>
            </div>

            {/* URL Input */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <label className="block text-sm font-semibold mb-2 text-slate-300">Target URL</label>
              <input
                type="url"
                placeholder="https://example.com"
                value={testUrl}
                onChange={(e) => setTestUrl(e.target.value)}
                className="w-full px-4 py-3 bg-slate-900 border border-slate-600 rounded-lg focus:border-blue-500 focus:outline-none"
              />
            </div>

            {/* Test Button */}
            <button
              onClick={handleTest}
              disabled={loading}
              className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl font-semibold flex items-center justify-center gap-2 disabled:opacity-50 transition transform hover:scale-105"
            >
              <PlayCircle className="w-5 h-5" />
              {loading ? 'Testing...' : 'Test Endpoint'}
            </button>
          </div>

          {/* Right: Response Section */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Response</h3>
              {result && (
                <span className={`px-3 py-1 rounded-full text-sm ${
                  result.success ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'
                }`}>
                  {result.success ? 'Success' : 'Error'}
                </span>
              )}
            </div>
            <div className="bg-slate-900 rounded-lg p-4 h-96 overflow-auto">
              {result ? (
                <pre className="text-sm text-slate-300 font-mono whitespace-pre-wrap">
                  {JSON.stringify(result, null, 2)}
                </pre>
              ) : (
                <div className="flex items-center justify-center h-full text-slate-500">
                  Response will appear here after testing
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="max-w-7xl mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center mb-12">Simple Pricing</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { name: 'Free', price: '$0', requests: '1,000', features: ['Basic endpoints', 'API documentation', 'Community support'] },
            { name: 'Pro', price: '$29', requests: '50,000', features: ['All endpoints', 'Priority support', 'Custom domains', 'Advanced analytics'], popular: true },
            { name: 'Enterprise', price: 'Custom', requests: 'Unlimited', features: ['Dedicated instance', '24/7 support', 'SLA guarantee', 'Custom integrations'] }
          ].map((plan, i) => (
            <div key={i} className={`relative bg-slate-800/50 border rounded-xl p-8 ${
              plan.popular ? 'border-blue-500' : 'border-slate-700'
            }`}>
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-blue-600 rounded-full text-sm font-semibold">
                  Most Popular
                </div>
              )}
              <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
              <div className="text-4xl font-bold mb-1">{plan.price}</div>
              <div className="text-slate-400 mb-6">{plan.requests} requests/month</div>
              <ul className="space-y-3 mb-8">
                {plan.features.map((f, j) => (
                  <li key={j} className="flex items-center gap-2">
                    <Check className="w-5 h-5 text-green-400" />
                    <span className="text-slate-300">{f}</span>
                  </li>
                ))}
              </ul>
              <button className={`w-full px-6 py-3 rounded-lg font-semibold transition ${
                plan.popular 
                  ? 'bg-blue-600 hover:bg-blue-700'
                  : 'bg-slate-700 hover:bg-slate-600'
              }`}>
                Get Started
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-700 mt-20">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Code className="w-6 h-6 text-blue-400" />
                <span className="text-xl font-bold">Crawlic</span>
              </div>
              <p className="text-slate-400 text-sm">Intelligent web scraping made simple</p>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Product</h4>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><a href="#" className="hover:text-white transition">Features</a></li>
                <li><a href="#" className="hover:text-white transition">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition">API Docs</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Company</h4>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><a href="#" className="hover:text-white transition">About</a></li>
                <li><a href="#" className="hover:text-white transition">Blog</a></li>
                <li><a href="#" className="hover:text-white transition">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Legal</h4>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><a href="#" className="hover:text-white transition">Privacy</a></li>
                <li><a href="#" className="hover:text-white transition">Terms</a></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-slate-700 flex items-center justify-between">
            <p className="text-slate-400 text-sm">© 2025 Crawlic. All rights reserved.</p>
            <div className="flex gap-4">
              <a href="#" className="text-slate-400 hover:text-white transition"><Github className="w-5 h-5" /></a>
              <a href="#" className="text-slate-400 hover:text-white transition"><Twitter className="w-5 h-5" /></a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}