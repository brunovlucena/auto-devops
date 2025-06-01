# 🤖 Auto-DevOps Landing Page

A modern, responsive landing page for Auto-DevOps AI infrastructure consulting services, built with Next.js 15 and featuring Jamie and Scarlet AI agents.

## ✨ Features

- **Modern Design**: Clean, professional design with smooth animations
- **Responsive**: Optimized for all devices (mobile, tablet, desktop)
- **Performance**: Built with Next.js 15 for optimal performance
- **Accessibility**: WCAG compliant with proper semantics
- **SEO Optimized**: Meta tags, structured data, and optimized content
- **TypeScript**: Full type safety throughout the application
- **Animations**: Smooth Framer Motion animations
- **Dark Mode Ready**: Theme system with light/dark mode support

## 🛠️ Tech Stack

- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS with custom design system
- **Components**: Shadcn/ui for consistent UI components
- **Animations**: Framer Motion for smooth interactions
- **Icons**: Lucide React for modern iconography
- **Type Safety**: TypeScript throughout
- **Deployment**: Optimized for Vercel deployment

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/bvlucena/auto-devops-landing.git
cd auto-devops-landing
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## 📁 Project Structure

```
auto-devops-landing/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Home page
│   ├── components/
│   │   ├── layout/             # Layout components
│   │   │   ├── header.tsx      # Navigation header
│   │   │   └── footer.tsx      # Site footer
│   │   ├── sections/           # Page sections
│   │   │   ├── hero-section.tsx
│   │   │   ├── features-section.tsx
│   │   │   ├── services-section.tsx
│   │   │   ├── testimonials-section.tsx
│   │   │   ├── pricing-section.tsx
│   │   │   └── contact-section.tsx
│   │   └── ui/                 # Reusable UI components
│   │       ├── button.tsx
│   │       └── card.tsx
│   └── lib/
│       └── utils.ts            # Utility functions
├── public/                     # Static assets
├── tailwind.config.ts          # Tailwind configuration
├── tsconfig.json              # TypeScript configuration
└── package.json               # Dependencies and scripts
```

## 🎨 Customization

### Colors and Theming

The design system uses CSS variables defined in `globals.css`. You can customize:

- Primary colors
- Secondary colors  
- Background variants
- Text colors
- Border styles

### Content Updates

Update the content in each section component:

- **Hero**: Modify `hero-section.tsx` for main messaging
- **Features**: Update features array in `features-section.tsx`
- **Services**: Customize services in `services-section.tsx`
- **Testimonials**: Add client testimonials in `testimonials-section.tsx`
- **Pricing**: Update pricing plans in `pricing-section.tsx`
- **Contact**: Modify contact methods in `contact-section.tsx`

### Animations

Animations are powered by Framer Motion. You can:

- Adjust animation timings
- Add new motion variants
- Customize scroll-triggered animations

## 📱 Responsive Design

The landing page is fully responsive with breakpoints:

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: > 1024px

## 🚀 Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Deploy automatically with every push

### Other Platforms

The site can be deployed to any platform supporting Next.js:

- Netlify
- AWS Amplify
- Railway
- DigitalOcean App Platform

## 📊 Performance

The landing page is optimized for:

- **Core Web Vitals**: Excellent scores across all metrics
- **SEO**: Proper meta tags and structured data
- **Accessibility**: WCAG 2.1 AA compliance
- **Bundle Size**: Optimized with Next.js automatic optimizations

## 🔗 Live Demo

- **Jamie AI Assistant**: [jamie.lucena.cloud](https://jamie.lucena.cloud)
- **Monitoring Dashboard**: [grafana.lucena.cloud](https://grafana.lucena.cloud)

## 📞 Contact

- **Email**: bruno@lucena.cloud
- **LinkedIn**: [linkedin.com/in/bvlucena](https://linkedin.com/in/bvlucena)
- **Phone**: +55 81 99131-9220

## 📄 License

This project is proprietary and confidential. All rights reserved.

---

Built with ❤️ for transforming infrastructure operations with AI.
