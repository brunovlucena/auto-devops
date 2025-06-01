"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Star, Quote } from "lucide-react"
import { motion } from "framer-motion"

const testimonials = [
  {
    name: "Sarah Chen",
    role: "CTO",
    company: "TechFlow Solutions",
    content: "Auto-DevOps transformed our infrastructure operations. We've achieved 99.9% uptime and reduced our operational overhead by 65%. Jamie has become an essential team member.",
    rating: 5,
    avatar: "/api/placeholder/40/40"
  },
  {
    name: "Marcus Rodriguez", 
    role: "DevOps Lead",
    company: "ScaleUp Inc",
    content: "The AI-powered monitoring with Scarlet prevented 8 major outages in our first month. The ROI was evident within weeks, not months.",
    rating: 5,
    avatar: "/api/placeholder/40/40"
  },
  {
    name: "Jennifer Wu",
    role: "VP of Engineering", 
    company: "CloudNative Corp",
    content: "Implementation was seamless. Our team went from skeptical to dependent on Jamie within days. The training and support were exceptional.",
    rating: 5,
    avatar: "/api/placeholder/40/40"
  },
  {
    name: "David Thompson",
    role: "Infrastructure Manager",
    company: "FinTech Pro",
    content: "Finally, a solution that actually delivers on its promises. Our incident response time dropped from hours to minutes.",
    rating: 5,
    avatar: "/api/placeholder/40/40"
  },
  {
    name: "Anna Kowalski",
    role: "Site Reliability Engineer",
    company: "DataStream Analytics", 
    content: "The proactive monitoring capabilities are game-changing. We now prevent issues before our customers even notice them.",
    rating: 5,
    avatar: "/api/placeholder/40/40"
  },
  {
    name: "James Miller",
    role: "Founding Engineer",
    company: "StartupX",
    content: "As a growing startup, Auto-DevOps allowed us to scale our infrastructure without scaling our DevOps team. Incredible value.",
    rating: 5,
    avatar: "/api/placeholder/40/40"
  }
]

export function TestimonialsSection() {
  return (
    <section className="py-24 bg-muted/30">
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
              What Our{" "}
              <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
                Clients Say
              </span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              See how engineering teams around the world are transforming their
              infrastructure operations with our AI-powered platform.
            </p>
          </motion.div>

          {/* Testimonials Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.name}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="group"
              >
                <Card className="h-full hover:shadow-lg transition-all duration-300 group-hover:-translate-y-1">
                  <CardContent className="p-6">
                    {/* Quote Icon */}
                    <Quote className="h-8 w-8 text-primary/20 mb-4" />
                    
                    {/* Rating */}
                    <div className="flex space-x-1 mb-4">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      ))}
                    </div>

                    {/* Content */}
                    <p className="text-muted-foreground mb-6 leading-relaxed">
                      "{testimonial.content}"
                    </p>

                    {/* Author */}
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-primary to-blue-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                        {testimonial.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <div className="font-semibold text-sm">{testimonial.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {testimonial.role} • {testimonial.company}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* Stats Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            viewport={{ once: true }}
            className="mt-16"
          >
            <div className="bg-gradient-to-r from-primary/5 to-blue-500/5 rounded-2xl p-8 border">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
                <div>
                  <div className="text-4xl font-bold text-primary mb-2">50+</div>
                  <div className="text-muted-foreground">Companies Transformed</div>
                </div>
                <div>
                  <div className="text-4xl font-bold text-green-500 mb-2">99.9%</div>
                  <div className="text-muted-foreground">Average Client Uptime</div>
                </div>
                <div>
                  <div className="text-4xl font-bold text-blue-500 mb-2">6 months</div>
                  <div className="text-muted-foreground">Average ROI Timeline</div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
} 