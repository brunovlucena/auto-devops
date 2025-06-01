"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bot, Shield, Clock, TrendingUp, AlertTriangle, Users, Monitor, Zap } from "lucide-react"
import { motion } from "framer-motion"

const features = [
  {
    icon: Bot,
    title: "Jamie - DevOps Expert",
    description: "24/7 intelligent assistant for your team",
    details: [
      "Custom-trained for your infrastructure",
      "Slack/Teams integration",
      "Instant, accurate responses",
      "Reduces escalation by 60%"
    ],
    color: "text-primary"
  },
  {
    icon: Shield,
    title: "Scarlet - Operations Guardian",
    description: "Autonomous infrastructure monitoring",
    details: [
      "Proactive monitoring & resolution",
      "Intelligent alerting system",
      "Self-healing capabilities",
      "Prevents 80% of outages"
    ],
    color: "text-red-500"
  },
  {
    icon: Clock,
    title: "Rapid Response",
    description: "< 2 minute average resolution time",
    details: [
      "Automated incident detection",
      "Immediate remediation",
      "Predictive maintenance",
      "24/7 availability"
    ],
    color: "text-green-500"
  },
  {
    icon: TrendingUp,
    title: "Business Impact",
    description: "Measurable ROI and efficiency gains",
    details: [
      "300-400% ROI in first year",
      "70% reduction in manual tasks",
      "99.9%+ uptime guarantee",
      "Cost optimization insights"
    ],
    color: "text-blue-500"
  },
  {
    icon: AlertTriangle,
    title: "Proactive Monitoring",
    description: "Prevent issues before they occur",
    details: [
      "Real-time system analysis",
      "Anomaly detection",
      "Capacity planning",
      "Performance optimization"
    ],
    color: "text-orange-500"
  },
  {
    icon: Users,
    title: "Team Enablement",
    description: "Empower your entire team",
    details: [
      "Comprehensive training included",
      "Knowledge transfer sessions",
      "95% team adoption rate",
      "Ongoing support"
    ],
    color: "text-purple-500"
  }
]

export function FeaturesSection() {
  return (
    <section id="features" className="py-24 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <div className="inline-flex items-center space-x-2 bg-primary/10 border border-primary/20 rounded-full px-4 py-2 text-sm mb-6">
              <Monitor className="h-4 w-4 text-primary" />
              <span className="text-primary font-medium">AI-Powered Platform</span>
            </div>
            <h2 className="text-3xl md:text-5xl font-bold mb-6">
              Meet Your{" "}
              <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
                AI Infrastructure
              </span>{" "}
              Team
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Jamie and Scarlet work together to transform your infrastructure operations,
              delivering unprecedented reliability and efficiency.
            </p>
          </motion.div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="group"
              >
                <Card className="h-full border-0 shadow-lg hover:shadow-xl transition-all duration-300 group-hover:-translate-y-2">
                  <CardHeader className="pb-4">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className={`w-12 h-12 bg-background rounded-xl flex items-center justify-center border ${feature.color}`}>
                        <feature.icon className={`h-6 w-6 ${feature.color}`} />
                      </div>
                      <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                    <CardDescription className="text-base">
                      {feature.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3">
                      {feature.details.map((detail, i) => (
                        <li key={i} className="flex items-start space-x-3">
                          <Zap className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-muted-foreground">{detail}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* Demo CTA */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            viewport={{ once: true }}
            className="text-center mt-16"
          >
            <div className="bg-gradient-to-r from-primary/10 to-blue-500/10 rounded-2xl p-8 border">
              <h3 className="text-2xl font-bold mb-4">Experience Our AI Platform Live</h3>
              <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
                Try our complete solution before you buy. See Jamie in action and explore
                our real-time monitoring dashboards.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a 
                  href="https://jamie.lucena.cloud" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="bg-primary text-primary-foreground hover:bg-primary/90 px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  Try Jamie AI Assistant →
                </a>
                <a 
                  href="https://grafana.lucena.cloud" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="bg-background border hover:bg-muted px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  View Monitoring Dashboard →
                </a>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
} 