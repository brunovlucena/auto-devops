import Link from "next/link"
import { Bot, Shield, Mail, Phone, Linkedin, Globe } from "lucide-react"

export function Footer() {
  return (
    <footer className="bg-muted/50 border-t">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <Link href="/" className="flex items-center space-x-2 mb-4">
              <div className="flex items-center space-x-1">
                <Bot className="h-8 w-8 text-primary" />
                <Shield className="h-6 w-6 text-blue-600" />
              </div>
              <span className="font-bold text-xl">Auto-DevOps</span>
            </Link>
            <p className="text-muted-foreground mb-4 max-w-md">
              Transform your infrastructure operations with intelligent AI agents. 
              Reduce operational overhead by 70% while improving system reliability.
            </p>
            <div className="flex space-x-4">
              <Link 
                href="mailto:bruno@lucena.cloud" 
                className="text-muted-foreground hover:text-primary transition-colors"
              >
                <Mail className="h-5 w-5" />
              </Link>
              <Link 
                href="https://linkedin.com/in/bvlucena" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-primary transition-colors"
              >
                <Linkedin className="h-5 w-5" />
              </Link>
              <Link 
                href="https://chat.lucena.cloud" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-primary transition-colors"
              >
                <Globe className="h-5 w-5" />
              </Link>
            </div>
          </div>

          {/* Services */}
          <div>
            <h3 className="font-semibold mb-4">Services</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link href="#services" className="hover:text-primary transition-colors">
                  AI Implementation
                </Link>
              </li>
              <li>
                <Link href="#services" className="hover:text-primary transition-colors">
                  Infrastructure Automation
                </Link>
              </li>
              <li>
                <Link href="#services" className="hover:text-primary transition-colors">
                  Team Training
                </Link>
              </li>
              <li>
                <Link href="#services" className="hover:text-primary transition-colors">
                  24/7 Support
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-semibold mb-4">Contact</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-center space-x-2">
                <Mail className="h-4 w-4" />
                <span>bruno@lucena.cloud</span>
              </li>
              <li className="flex items-center space-x-2">
                <Phone className="h-4 w-4" />
                <span>+55 81 99131-9220</span>
              </li>
              <li>
                <Link 
                  href="https://jamie.lucena.cloud" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors"
                >
                  Try Jamie Demo
                </Link>
              </li>
              <li>
                <Link 
                  href="https://grafana.lucena.cloud" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors"
                >
                  Monitoring Demo
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t mt-8 pt-8 text-center text-sm text-muted-foreground">
          <p>© 2024 Auto-DevOps Consulting. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
} 