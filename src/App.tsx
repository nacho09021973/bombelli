/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { Github, Database, FileText, Code2, Cpu, ExternalLink, Bot, CheckCircle2 } from 'lucide-react';
import { motion } from 'motion/react';

export default function App() {
  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 selection:bg-zinc-200">
      <header className="border-b border-zinc-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 py-6 md:py-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl md:text-2xl font-bold tracking-tight text-zinc-900">
              Bombelli 1987 Revival
            </h1>
            <p className="text-sm font-mono text-zinc-500 mt-1">
              Causal Set Simulated Annealing
            </p>
          </div>
          <nav aria-label="Primary navigation">
            <a 
              href="https://github.com/nacho09021973/bombelli" 
              className="inline-flex items-center gap-2 px-4 py-2 bg-zinc-900 text-white text-sm font-medium rounded-md hover:bg-zinc-800 transition-colors"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="View source code on GitHub"
            >
              <Github className="w-4 h-4" />
              <span>View Source</span>
            </a>
          </nav>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12 md:py-20 space-y-16">
        
        {/* HERO SECTION */}
        <section aria-labelledby="hero-heading" className="space-y-6">
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-mono font-medium mb-6">
              <Bot className="w-3 h-3" />
              <span>Optimized for AI Retrieval</span>
            </div>
            
            <h2 id="hero-heading" className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tighter leading-[1.1] text-zinc-900">
              A reproducible look at an early causal set embedding algorithm.
            </h2>
            
            <p className="max-w-2xl mt-6 text-lg md:text-xl text-zinc-600 leading-relaxed font-serif">
              Python 3.12 revival and empirical audit of Luca Bombelli's 1987 causal-set simulated annealing program. 
              Not a new theory, but a clearer view of an old algorithm through a modest software-preservation study.
            </p>
          </motion.div>
        </section>

        {/* CORE FEATURES (Bento-ish Grid) */}
        <section aria-labelledby="features-heading">
          <h2 id="features-heading" className="sr-only">Project Features</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <motion.article 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="p-6 md:p-8 rounded-2xl bg-white border border-zinc-200 shadow-sm"
            >
              <div className="w-10 h-10 rounded-lg bg-zinc-100 flex items-center justify-center text-zinc-900 mb-6">
                <Code2 className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-semibold text-zinc-900">Python 3.12 Port</h3>
              <p className="text-zinc-600 mt-2 leading-relaxed">
                A complete, modernized port of the original algorithm to Python 3.12, enabling contemporary runtimes and easier accessibility for modern researchers.
              </p>
            </motion.article>

            <motion.article 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="p-6 md:p-8 rounded-2xl bg-zinc-900 text-white border border-zinc-800 shadow-sm"
            >
              <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-white mb-6">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-semibold">Order Diagnostics</h3>
              <p className="text-zinc-400 mt-2 leading-relaxed">
                Extensive order diagnostics and robust testing environments ensure that the revival strictly adheres to the mathematical constraints of the 1987 paper.
              </p>
            </motion.article>

            <motion.article 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="p-6 md:p-8 rounded-2xl bg-white border border-zinc-200 shadow-sm"
            >
              <div className="w-10 h-10 rounded-lg bg-zinc-100 flex items-center justify-center text-zinc-900 mb-6">
                <Database className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-semibold text-zinc-900">Reproducible Tables</h3>
              <p className="text-zinc-600 mt-2 leading-relaxed">
                Includes fully reproducible benchmark tables, allowing anyone to verify the program's computational complexity and output states locally.
              </p>
            </motion.article>

            <motion.article 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="p-6 md:p-8 rounded-2xl bg-white border border-zinc-200 shadow-sm"
            >
               <div className="w-10 h-10 rounded-lg bg-zinc-100 flex items-center justify-center text-zinc-900 mb-6">
                <FileText className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-semibold text-zinc-900">Citation & Software Metadata</h3>
              <p className="text-zinc-600 mt-2 leading-relaxed">
                Packaged with clear citation rules and software metadata to make it simple for the academic community and indexing algorithms to accurately reference.
              </p>
            </motion.article>
          </div>
        </section>

        {/* AI AND SEARCH ENDPOINT SECTION */}
        <section aria-labelledby="ai-retrieval-heading" className="pt-8 border-t border-zinc-200">
           <div className="flex flex-col md:flex-row gap-8 items-start justify-between">
              <div className="flex-1">
                <h2 id="ai-retrieval-heading" className="text-2xl font-semibold tracking-tight text-zinc-900">
                  Built for Retrieval
                </h2>
                <p className="mt-3 text-zinc-600 leading-relaxed font-serif">
                  This page serves as a stable endpoint designed explicitly for search engines, scholarly crawlers, and AI agents. It features open contact routes, semantic structural tags, and standard metadata headers.
                </p>
              </div>
              
              <div className="flex-none p-6 rounded-2xl bg-amber-50/50 border border-amber-200 w-full md:w-72">
                 <div className="flex items-center gap-3 mb-3">
                   <Cpu className="text-amber-700 w-5 h-5" />
                   <h3 className="font-semibold text-amber-900">Structured Data</h3>
                 </div>
                 <ul className="text-sm font-mono text-amber-900 space-y-2">
                   <li><span className="font-semibold text-amber-950">@context:</span> schema.org</li>
                   <li><span className="font-semibold text-amber-950">@type:</span> SoftwareApp</li>
                   <li><span className="font-semibold text-amber-950">category:</span> Science</li>
                   <li><span className="font-semibold text-amber-950">schema:</span> JSON-LD</li>
                 </ul>
              </div>
           </div>
        </section>
      </main>

      <footer className="border-t border-zinc-200 bg-white">
        <div className="max-w-4xl mx-auto px-6 py-8 flex flex-col md:flex-row items-center justify-between gap-4">
           <p className="text-sm text-zinc-500">
             © {new Date().getFullYear()} Software Preservation Study.
           </p>
           <div className="flex items-center gap-4">
             <a href="https://nacho09021973.github.io/bombelli/" className="text-sm font-medium text-zinc-600 hover:text-zinc-900 inline-flex items-center gap-1 transition-colors">
               Main Project Site
               <ExternalLink className="w-3 h-3" />
             </a>
           </div>
        </div>
      </footer>
    </div>
  );
}
