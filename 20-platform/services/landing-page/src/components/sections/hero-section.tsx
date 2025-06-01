"use client"

import { Button } from "@/components/ui/button"
import { ArrowRight, CheckCircle, Bot, Shield, Zap } from "lucide-react"
import Link from "next/link"
import { motion } from "framer-motion"

export function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-muted/30">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      <div className="absolute top-20 left-20 w-72 h-72 bg-primary/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-20 right-20 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>

      <div className="container mx-auto px-4 py-20 relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="space-y-8"
            >
              {/* Badge */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="inline-flex items-center space-x-2 bg-primary/10 border border-primary/20 rounded-full px-4 py-2 text-sm"
              >
                <Zap className="h-4 w-4 text-primary" />
                <span className="text-primary font-medium">AI-Powered Infrastructure Management</span>
              </motion.div>

              {/* Main Headline */}
              <div className="space-y-4">
                <h1 className="text-4xl md:text-6xl font-bold leading-tight">
                  Transform Your{" "}
                  <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
                    Infrastructure
                  </span>{" "}
                  with AI
                </h1>
                <p className="text-xl text-muted-foreground leading-relaxed">
                  Reduce operational overhead by <strong>70%</strong> while achieving{" "}
                  <strong>99.9%+ uptime</strong> with our intelligent AI agents{" "}
                  <strong>Jamie</strong> and <strong>Scarlet</strong>.
                </p>
              </div>

              {/* Key Benefits */}
              <div className="space-y-3">
                {[
                  "80% reduction in manual incident resolution",
                  "90% faster problem identification and fixes", 
                  "ROI of 300% within first 6 months"
                ].map((benefit, index) => (
                  <motion.div
                    key={benefit}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.1, duration: 0.5 }}
                    className="flex items-center space-x-3"
                  >
                    <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                    <span className="text-muted-foreground">{benefit}</span>
                  </motion.div>
                ))}
              </div>

              {/* CTAs */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8, duration: 0.5 }}
                className="flex flex-col sm:flex-row gap-4"
              >
                <Button size="xl" variant="gradient" className="group">
                  Get Free Assessment
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
                <Link href="https://jamie.lucena.cloud" target="_blank" rel="noopener noreferrer">
                  <Button size="xl" variant="outline" className="w-full sm:w-auto">
                    Try Jamie Demo
                  </Button>
                </Link>
              </motion.div>

              {/* Social Proof */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1, duration: 0.5 }}
                className="pt-8"
              >
                <p className="text-sm text-muted-foreground mb-4">Trusted by technology companies worldwide</p>
                <div className="flex items-center space-x-8 opacity-60">
                  <div className="text-sm font-medium">50-500 Engineers</div>
                  <div className="text-sm font-medium">SaaS Platforms</div>
                  <div className="text-sm font-medium">Financial Services</div>
                </div>
              </motion.div>
            </motion.div>

            {/* Right Content - AI Agents Visualization */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3, duration: 0.8 }}
              className="relative"
            >
              <div className="relative max-w-lg mx-auto">
                {/* Jamie Card */}
                <motion.div
                  animate={{ y: [0, -10, 0] }}
                  transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                  className="bg-card/80 backdrop-blur border rounded-2xl p-6 shadow-xl"
                >
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
                      <Bot className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Jamie</h3>
                      <p className="text-sm text-muted-foreground">DevOps Assistant</p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">
                    "Analyzing system metrics... Kubernetes cluster optimization recommended."
                  </p>
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-xs text-green-500">Active</span>
                  </div>
                </motion.div>

                {/* Scarlet Card */}
                <motion.div
                  animate={{ y: [0, 10, 0] }}
                  transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                  className="bg-card/80 backdrop-blur border rounded-2xl p-6 shadow-xl mt-6 ml-8"
                >
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-12 h-12 bg-red-500/10 rounded-xl flex items-center justify-center">
                      <Shield className="h-6 w-6 text-red-500" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Scarlet</h3>
                      <p className="text-sm text-muted-foreground">Infrastructure Guardian</p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">
                    "Prevented 3 potential outages. Auto-scaling triggered for peak traffic."
                  </p>
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                    <span className="text-xs text-red-500">Monitoring</span>
                  </div>
                </motion.div>

                {/* Connecting Lines */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-px h-24 bg-gradient-to-b from-primary to-red-500 opacity-30"></div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  )
} 