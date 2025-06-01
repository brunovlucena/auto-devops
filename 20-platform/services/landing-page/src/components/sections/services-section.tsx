"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle, Settings, Rocket, BookOpen, Shield } from "lucide-react"
import { motion } from "framer-motion"

const services = [
  {
    icon: Settings,
    title: "Complete Implementation",
    description: "End-to-end setup tailored to your infrastructure",
    features: [
      "Custom deployment for your environment",
      "Integration with existing tools",
      "Team training and knowledge transfer",
      "Performance monitoring & ROI tracking"
    ],
    timeline: "6-8 weeks"
  },
  {
    icon: Rocket,
    title: "Rapid Deployment",
    description: "Get up and running in record time",
    features: [
      "Kubernetes cluster setup",
      "Jamie & Scarlet implementation",
      "Chat platform integration",
      "Initial testing and validation"
    ],
    timeline: "3-4 weeks"
  },
  {
    icon: BookOpen,
    title: "Team Enablement",
    description: "Comprehensive training and support",
    features: [
      "Custom training sessions",
      "Documentation and best practices",
      "Knowledge base population",
      "95% team adoption guarantee"
    ],
    timeline: "2 weeks"
  },
  {
    icon: Shield,
    title: "Ongoing Support",
    description: "Continuous optimization and assistance",
    features: [
      "24/7 monitoring and support",
      "Regular performance reviews",
      "Feature updates and optimization",
      "Dedicated success manager"
    ],
    timeline: "Ongoing"
  }
]

const methodology = [
  {
    phase: "Phase 1",
    title: "Assessment & Design",
    duration: "Week 1-2",
    activities: [
      "Infrastructure audit and readiness assessment",
      "Custom architecture design",
      "Integration planning with existing tools",
      "Team skill assessment and training plan"
    ]
  },
  {
    phase: "Phase 2", 
    title: "Core Deployment",
    duration: "Week 3-4",
    activities: [
      "Kubernetes cluster setup and configuration",
      "Jamie deployment with custom training data",
      "Scarlet implementation with monitoring integration",
      "Initial testing and validation"
    ]
  },
  {
    phase: "Phase 3",
    title: "Integration & Training",
    duration: "Week 5-6", 
    activities: [
      "Chat platform integration (Slack/Teams)",
      "Existing tool connections (Jira, GitHub, etc.)",
      "Team training sessions and documentation",
      "Knowledge base population with your processes"
    ]
  },
  {
    phase: "Phase 4",
    title: "Optimization & Handover",
    duration: "Week 7-8",
    activities: [
      "Performance tuning and optimization",
      "Advanced feature configuration", 
      "Full team knowledge transfer",
      "Go-live support and monitoring"
    ]
  }
]

export function ServicesSection() {
  return (
    <section id="services" className="py-24">
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
            <h2 className="text-3xl md:text-5xl font-bold mb-6">
              Our{" "}
              <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
                Service Offering
              </span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              From assessment to deployment and ongoing support, we handle everything
              to ensure your AI infrastructure transformation is successful.
            </p>
          </motion.div>

          {/* Services Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
            {services.map((service, index) => (
              <motion.div
                key={service.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-4">
                    <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-4">
                      <service.icon className="h-6 w-6 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{service.title}</CardTitle>
                    <CardDescription>{service.description}</CardDescription>
                    <div className="text-sm font-medium text-primary mt-2">
                      {service.timeline}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {service.features.map((feature, i) => (
                        <li key={i} className="flex items-start space-x-2">
                          <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-muted-foreground">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* Implementation Methodology */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="mb-16"
          >
            <h3 className="text-2xl md:text-3xl font-bold text-center mb-12">
              Implementation Methodology
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {methodology.map((phase, index) => (
                <motion.div
                  key={phase.phase}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.15 }}
                  viewport={{ once: true }}
                  className="relative"
                >
                  <Card className="h-full">
                    <CardHeader className="pb-4">
                      <div className="flex items-center space-x-3 mb-2">
                        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground text-sm font-bold">
                          {index + 1}
                        </div>
                        <span className="text-sm font-medium text-primary">{phase.phase}</span>
                      </div>
                      <CardTitle className="text-lg">{phase.title}</CardTitle>
                      <div className="text-sm text-muted-foreground">{phase.duration}</div>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {phase.activities.map((activity, i) => (
                          <li key={i} className="text-sm text-muted-foreground flex items-start space-x-2">
                            <div className="w-1.5 h-1.5 bg-primary rounded-full flex-shrink-0 mt-2"></div>
                            <span>{activity}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                  {/* Connecting line for desktop */}
                  {index < methodology.length - 1 && (
                    <div className="hidden lg:block absolute top-8 -right-3 w-6 h-0.5 bg-gradient-to-r from-primary to-primary/20"></div>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Results Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <div className="bg-gradient-to-r from-green-500/10 to-blue-500/10 rounded-2xl p-8 border">
              <h3 className="text-2xl font-bold mb-6">Proven Results</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div>
                  <div className="text-3xl font-bold text-green-500 mb-2">80%</div>
                  <div className="text-sm text-muted-foreground">Reduction in manual incident resolution</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-blue-500 mb-2">90%</div>
                  <div className="text-sm text-muted-foreground">Faster problem identification</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-purple-500 mb-2">99.9%</div>
                  <div className="text-sm text-muted-foreground">Uptime achievement</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-orange-500 mb-2">300%</div>
                  <div className="text-sm text-muted-foreground">ROI within 6 months</div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
} 