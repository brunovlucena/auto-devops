"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle, ArrowRight, Calculator, DollarSign } from "lucide-react"
import { motion } from "framer-motion"

const pricingPlans = [
  {
    name: "Implementation Services",
    price: "$75,000 - $150,000",
    description: "Complete AI infrastructure transformation",
    features: [
      "Infrastructure audit & assessment",
      "Custom Jamie & Scarlet deployment",
      "Team training & knowledge transfer",
      "Integration with existing tools",
      "Performance monitoring setup",
      "Go-live support"
    ],
    timeline: "6-8 weeks",
    popular: false
  },
  {
    name: "Monthly Support",
    price: "$15,000 - $30,000/month",
    description: "Ongoing optimization and support",
    features: [
      "24/7 monitoring & support",
      "Regular performance reviews",
      "Feature updates & optimization",
      "Dedicated success manager",
      "Priority technical support",
      "Monthly ROI reporting"
    ],
    timeline: "Ongoing",
    popular: true
  }
]

const roiMetrics = [
  {
    category: "Operational Cost Savings",
    amount: "$200,000 - $500,000",
    period: "6-month period",
    description: "Reduced manual operations and faster resolution"
  },
  {
    category: "Downtime Prevention",
    amount: "$100,000 - $1M+",
    period: "6-month period", 
    description: "Proactive issue prevention and rapid response"
  },
  {
    category: "Team Productivity Gains",
    amount: "$150,000 - $300,000",
    period: "6-month period",
    description: "Focus on innovation vs. firefighting"
  }
]

export function PricingSection() {
  return (
    <section id="pricing" className="py-24">
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
            <div className="inline-flex items-center space-x-2 bg-green-500/10 border border-green-500/20 rounded-full px-4 py-2 text-sm mb-6">
              <DollarSign className="h-4 w-4 text-green-500" />
              <span className="text-green-500 font-medium">Transparent Pricing</span>
            </div>
            <h2 className="text-3xl md:text-5xl font-bold mb-6">
              Investment &{" "}
              <span className="bg-gradient-to-r from-green-500 to-blue-600 bg-clip-text text-transparent">
                ROI
              </span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Our transparent pricing model ensures you know exactly what you're
              investing in and the returns you can expect.
            </p>
          </motion.div>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
            {pricingPlans.map((plan, index) => (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
                className="relative"
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-primary text-primary-foreground px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                <Card className={`h-full ${plan.popular ? 'border-primary shadow-lg' : ''}`}>
                  <CardHeader className="pb-4">
                    <CardTitle className="text-2xl">{plan.name}</CardTitle>
                    <div className="text-3xl font-bold text-primary mb-2">{plan.price}</div>
                    <CardDescription className="text-base">{plan.description}</CardDescription>
                    <div className="text-sm font-medium text-muted-foreground">
                      Timeline: {plan.timeline}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3 mb-6">
                      {plan.features.map((feature, i) => (
                        <li key={i} className="flex items-start space-x-3">
                          <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-sm">{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <Button 
                      className="w-full" 
                      variant={plan.popular ? "default" : "outline"}
                      size="lg"
                    >
                      Get Started
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* ROI Breakdown */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            viewport={{ once: true }}
            className="mb-16"
          >
            <h3 className="text-2xl md:text-3xl font-bold text-center mb-12">
              Expected Returns (6-month period)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {roiMetrics.map((metric, index) => (
                <motion.div
                  key={metric.category}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Card className="text-center h-full">
                    <CardHeader>
                      <CardTitle className="text-lg">{metric.category}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl font-bold text-green-500 mb-2">
                        {metric.amount}
                      </div>
                      <div className="text-sm text-muted-foreground mb-4">
                        {metric.period}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {metric.description}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* ROI Summary */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <div className="bg-gradient-to-r from-green-500/10 to-blue-500/10 rounded-2xl p-8 border">
              <div className="flex items-center justify-center space-x-2 mb-6">
                <Calculator className="h-6 w-6 text-green-500" />
                <h3 className="text-2xl font-bold">Typical ROI</h3>
              </div>
              <div className="text-5xl font-bold text-green-500 mb-4">300-400%</div>
              <div className="text-xl text-muted-foreground mb-6">Return on Investment in First Year</div>
              <p className="text-muted-foreground max-w-2xl mx-auto mb-8">
                Most clients see ROI within 6 months, with cumulative benefits
                continuing to grow as the AI systems learn and optimize your infrastructure.
              </p>
              <Button size="xl" variant="gradient" className="group">
                Schedule Free Assessment
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
} 