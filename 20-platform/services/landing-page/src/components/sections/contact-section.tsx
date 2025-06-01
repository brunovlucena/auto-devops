"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Mail, Phone, Calendar, MessageSquare, CheckCircle, ArrowRight } from "lucide-react"
import { motion } from "framer-motion"

const contactMethods = [
  {
    icon: Mail,
    title: "Email",
    value: "bruno@lucena.cloud",
    description: "Get in touch for detailed discussions",
    action: "mailto:bruno@lucena.cloud"
  },
  {
    icon: Phone,
    title: "Phone",
    value: "+55 81 99131-9220",
    description: "Direct line for urgent inquiries",
    action: "tel:+5581991319220"
  },
  {
    icon: MessageSquare,
    title: "LinkedIn",
    value: "linkedin.com/in/bvlucena",
    description: "Connect and message on LinkedIn",
    action: "https://linkedin.com/in/bvlucena"
  },
  {
    icon: Calendar,
    title: "Schedule Call",
    value: "Book consultation",
    description: "Schedule a free 30-minute assessment",
    action: "#"
  }
]

const assessmentItems = [
  "Infrastructure audit and readiness assessment",
  "Custom ROI projection based on your metrics", 
  "Implementation roadmap tailored for your organization",
  "Optional 2-week proof of concept demonstration"
]

export function ContactSection() {
  return (
    <section id="contact" className="py-24 bg-muted/30">
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
              Ready to{" "}
              <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
                Transform
              </span>{" "}
              Your Infrastructure?
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Start with a free assessment and see how Auto-DevOps can revolutionize
              your team's productivity and system reliability.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Free Assessment Card */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <Card className="h-full">
                <CardHeader>
                  <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-4">
                    <CheckCircle className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-2xl">Free Assessment</CardTitle>
                  <CardDescription className="text-base">
                    No obligation - Understand your transformation potential
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4 mb-8">
                    {assessmentItems.map((item, index) => (
                      <motion.div
                        key={item}
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5, delay: index * 0.1 }}
                        viewport={{ once: true }}
                        className="flex items-start space-x-3"
                      >
                        <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-muted-foreground">{item}</span>
                      </motion.div>
                    ))}
                  </div>
                  
                  <div className="space-y-4">
                    <Button size="lg" variant="gradient" className="w-full group">
                      Schedule Free Assessment
                      <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                    </Button>
                    <p className="text-xs text-muted-foreground text-center">
                      2-hour deep dive into your current setup • Custom ROI projection • No commitment required
                    </p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Contact Methods */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="space-y-6"
            >
              <div>
                <h3 className="text-2xl font-bold mb-6">Get In Touch</h3>
                <p className="text-muted-foreground mb-8">
                  Prefer to connect directly? Reach out through any of these channels.
                  I personally handle all inquiries and consultations.
                </p>
              </div>

              <div className="grid grid-cols-1 gap-4">
                {contactMethods.map((method, index) => (
                  <motion.a
                    key={method.title}
                    href={method.action}
                    target={method.action.startsWith('http') ? '_blank' : undefined}
                    rel={method.action.startsWith('http') ? 'noopener noreferrer' : undefined}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    viewport={{ once: true }}
                    className="group"
                  >
                    <Card className="hover:shadow-lg transition-all duration-300 group-hover:-translate-y-1 border-0 bg-background/50">
                      <CardContent className="p-6">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                            <method.icon className="h-6 w-6 text-primary" />
                          </div>
                          <div className="flex-1">
                            <div className="font-semibold text-sm">{method.title}</div>
                            <div className="text-primary font-medium">{method.value}</div>
                            <div className="text-xs text-muted-foreground">{method.description}</div>
                          </div>
                          <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                        </div>
                      </CardContent>
                    </Card>
                  </motion.a>
                ))}
              </div>

              {/* Demo Links */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                viewport={{ once: true }}
                className="pt-6 border-t"
              >
                <h4 className="font-semibold mb-4">Try Our Platform</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <a 
                    href="https://jamie.lucena.cloud" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center space-x-3 p-4 bg-primary/5 rounded-lg hover:bg-primary/10 transition-colors group"
                  >
                    <div className="w-8 h-8 bg-primary/20 rounded-lg flex items-center justify-center">
                      <MessageSquare className="h-4 w-4 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-sm">Jamie AI Assistant</div>
                      <div className="text-xs text-muted-foreground">Interactive demo</div>
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
                  </a>
                  
                  <a 
                    href="https://grafana.lucena.cloud" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center space-x-3 p-4 bg-blue-500/5 rounded-lg hover:bg-blue-500/10 transition-colors group"
                  >
                    <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                      <Calendar className="h-4 w-4 text-blue-500" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-sm">Monitoring Dashboard</div>
                      <div className="text-xs text-muted-foreground">Live infrastructure</div>
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
                  </a>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  )
} 