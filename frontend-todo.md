# Kalori Makanan API - Frontend Todo 🍽️

## 📋 Project Overview
Create a simple, clean Next.js frontend for the Kalori Makanan API that will be deployed as a separate repository on Netlify. The focus is on simplicity - a beautiful landing page with basic documentation and easy access to the API.

**Live API**: https://kalori-makanan-kkm.onrender.com  
**API Docs**: https://kalori-makanan-kkm.onrender.com/docs

---

## 🛠️ Tech Stack

### Core
- **Next.js 14** (App Router)
- **TypeScript** (for type safety)
- **Tailwind CSS** (for styling)
- **React 18** (latest)

### Additional
- **SWR** or **TanStack Query** (for API calls)
- **Framer Motion** (for subtle animations)
- **Lucide React** (for icons)
- **next-themes** (optional dark mode)

### Deployment
- **Netlify** (static deployment)
- **GitHub** (source control)

---

## 🚀 Project Setup

### 1. Initialize Project
```bash
npx create-next-app@latest kalori-makanan-frontend --typescript --tailwind --eslint --app
cd kalori-makanan-frontend
```

### 2. Install Dependencies
```bash
npm install swr framer-motion lucide-react clsx
npm install --save-dev @types/node
```

### 3. Environment Setup
```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=https://kalori-makanan-kkm.onrender.com
```

### 4. Git Setup
```bash
git init
git add .
git commit -m "Initial commit"
# Push to GitHub repository
```

---

## 📁 Project Structure

```
kalori-makanan-frontend/
├── app/
│   ├── globals.css
│   ├── layout.tsx
│   ├── page.tsx                 # Landing page
│   ├── docs/
│   │   └── page.tsx            # Documentation page
│   └── examples/
│       └── page.tsx            # API examples page
├── components/
│   ├── ui/
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── badge.tsx
│   ├── layout/
│   │   ├── header.tsx
│   │   ├── footer.tsx
│   │   └── navigation.tsx
│   ├── sections/
│   │   ├── hero.tsx
│   │   ├── features.tsx
│   │   ├── stats.tsx
│   │   ├── api-demo.tsx
│   │   └── cta.tsx
│   └── api/
│       ├── search-demo.tsx
│       └── code-examples.tsx
├── lib/
│   ├── api.ts                  # API client
│   ├── types.ts               # TypeScript types
│   └── utils.ts               # Utility functions
├── public/
│   ├── favicon.ico
│   └── og-image.png
└── README.md
```

---

## 🎨 Design Guidelines

### Color Palette
```css
/* Primary Colors */
--primary: #4299e1;      /* Blue */
--primary-dark: #3182ce;
--secondary: #48bb78;    /* Green */
--accent: #ed8936;       /* Orange */

/* Neutral Colors */
--gray-50: #f7fafc;
--gray-100: #edf2f7;
--gray-200: #e2e8f0;
--gray-600: #718096;
--gray-900: #1a202c;
```

### Typography
- **Headings**: font-bold, clean hierarchy
- **Body**: font-normal, readable line-height
- **Code**: font-mono, proper syntax highlighting

### Design Principles
- **Clean & Minimal**: No unnecessary elements
- **Mobile-First**: Responsive design
- **Fast Loading**: Optimized images and code
- **Accessible**: Proper contrast and semantics

---

## 📄 Pages & Components

### 1. Landing Page (`app/page.tsx`)

#### Hero Section
- [ ] Eye-catching headline: "Fast & Reliable Food Calorie API"
- [ ] Subtitle: "750+ Malaysian & International Foods"
- [ ] Primary CTA: "Get API Access" → links to `/docs`
- [ ] Secondary CTA: "View Documentation" → links to `https://kalori-makanan-kkm.onrender.com/docs`

#### Stats Section
- [ ] **750+** Food Items
- [ ] **11** Categories
- [ ] **REST** API Standard
- [ ] **99.9%** Uptime

#### Features Section
- [ ] 🔍 **Food Search** - Search by name
- [ ] 📊 **Calorie Data** - Detailed nutrition info
- [ ] 🏷️ **Categories** - Organized food groups
- [ ] 📱 **REST API** - Easy integration
- [ ] 📚 **Auto Docs** - Swagger & ReDoc
- [ ] 🚀 **Production Ready** - Deployed & reliable

#### Live Demo Section
- [ ] Simple search input
- [ ] "Try searching: nasi lemak, rendang, ayam"
- [ ] Display search results in cards
- [ ] Show API response example

#### Code Examples Section
```bash
# Quick examples
curl "https://kalori-makanan-kkm.onrender.com/foods/search?name=nasi%20lemak"
```

#### CTA Section
- [ ] "Ready to integrate?"
- [ ] "Get API Access" button → docs
- [ ] "View Examples" button → examples page

### 2. Documentation Page (`app/docs/page.tsx`)

#### Getting Started
- [ ] Base URL: `https://kalori-makanan-kkm.onrender.com`
- [ ] No authentication required
- [ ] Rate limiting info
- [ ] Response format explanation

#### Endpoints Overview
- [ ] **GET** `/health` - Health check
- [ ] **GET** `/foods/search?name={name}` - Search foods
- [ ] **GET** `/foods/{id}` - Get food by ID
- [ ] **GET** `/foods` - List all foods (paginated)
- [ ] **GET** `/categories` - List categories
- [ ] **GET** `/foods/search/{name}/calories` - Quick calorie lookup

#### Response Examples
- [ ] Show JSON response structure
- [ ] Error handling examples
- [ ] Pagination details

#### SDKs & Libraries
- [ ] JavaScript/TypeScript examples
- [ ] Python examples
- [ ] cURL examples
- [ ] Links to Swagger docs

### 3. Examples Page (`app/examples/page.tsx`)

#### Interactive Examples
- [ ] Food search with live results
- [ ] Category browsing
- [ ] Individual food lookup
- [ ] Pagination demo

#### Code Snippets
- [ ] Copy-to-clipboard functionality
- [ ] Multiple language examples
- [ ] Real API responses

---

## 🔌 API Integration

### API Client (`lib/api.ts`)
```typescript
// Base configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

// API functions
export const searchFoods = async (name: string) => { /* implementation */ }
export const getFoodById = async (id: number) => { /* implementation */ }
export const getCategories = async () => { /* implementation */ }
export const getHealthStatus = async () => { /* implementation */ }
```

### TypeScript Types (`lib/types.ts`)
```typescript
// Based on Pydantic models from backend
export interface Food {
  id: number;
  name: string;
  serving?: string;
  weight_g?: number;
  calories_kcal?: number;
  reference?: string;
  category?: string;
}

export interface FoodSearchResponse {
  total: number;
  foods: Food[];
}

export interface Category {
  id: number;
  name: string;
}

export interface HealthCheck {
  status: string;
  message: string;
  database_connected: boolean;
}
```

---

## 🎯 Feature Checklist

### Phase 1: Core Setup
- [ ] Create Next.js project with TypeScript
- [ ] Set up Tailwind CSS
- [ ] Create basic project structure
- [ ] Set up environment variables
- [ ] Create GitHub repository

### Phase 2: API Integration
- [ ] Create API client functions
- [ ] Define TypeScript types
- [ ] Add error handling
- [ ] Test API connections
- [ ] Add loading states

### Phase 3: UI Components
- [ ] Create reusable UI components (Button, Card, Badge)
- [ ] Build layout components (Header, Footer)
- [ ] Add navigation
- [ ] Implement responsive design
- [ ] Add icons and styling

### Phase 4: Landing Page
- [ ] Hero section with CTA
- [ ] Stats section with live data
- [ ] Features showcase
- [ ] Live search demo
- [ ] Code examples
- [ ] Final CTA section

### Phase 5: Documentation
- [ ] Getting started guide
- [ ] Endpoint documentation
- [ ] Response examples
- [ ] Error handling guide
- [ ] Integration examples

### Phase 6: Examples Page
- [ ] Interactive API demo
- [ ] Code snippets
- [ ] Copy-to-clipboard
- [ ] Multiple language examples
- [ ] Live API responses

### Phase 7: Polish & Optimization
- [ ] SEO optimization (metadata, sitemap)
- [ ] Performance optimization
- [ ] Accessibility improvements
- [ ] Mobile responsiveness testing
- [ ] Cross-browser testing

### Phase 8: Deployment
- [ ] Configure Netlify deployment
- [ ] Set up continuous deployment
- [ ] Configure environment variables
- [ ] Add custom domain (optional)
- [ ] Set up analytics (optional)

---

## 🚀 Deployment to Netlify

### 1. Build Configuration
```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = "out"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### 2. Environment Variables
- Add `NEXT_PUBLIC_API_BASE_URL` in Netlify dashboard
- Set to `https://kalori-makanan-kkm.onrender.com`

### 3. Next.js Configuration
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig
```

### 4. Deployment Steps
- [ ] Connect GitHub repository to Netlify
- [ ] Configure build settings
- [ ] Set environment variables
- [ ] Deploy and test
- [ ] Configure custom domain (optional)

---

## 📝 Content Guidelines

### Tone & Voice
- **Professional** but approachable
- **Clear** and concise
- **Developer-friendly** language
- **Helpful** and supportive

### Key Messages
- "Simple & reliable food calorie API"
- "750+ Malaysian & international foods"
- "Ready for production use"
- "Easy integration"
- "Comprehensive documentation"

### Call-to-Actions
- **Primary**: "Get API Access" → API docs
- **Secondary**: "View Examples" → examples page
- **Tertiary**: "Browse Documentation" → internal docs

---

## 🎯 Success Metrics

### Performance Goals
- [ ] Page load time < 3 seconds
- [ ] Lighthouse score > 90
- [ ] Mobile-friendly design
- [ ] Zero accessibility errors

### User Experience Goals
- [ ] Clear navigation
- [ ] Easy-to-find API documentation
- [ ] Working live examples
- [ ] Copy-paste ready code snippets

### SEO Goals
- [ ] Proper meta tags
- [ ] Structured data
- [ ] XML sitemap
- [ ] Social media cards

---

## 🔗 Important Links

- **Backend API**: https://kalori-makanan-kkm.onrender.com
- **API Documentation**: https://kalori-makanan-kkm.onrender.com/docs
- **ReDoc**: https://kalori-makanan-kkm.onrender.com/redoc
- **Backend Repository**: (current repo)
- **Frontend Repository**: (to be created)

---

## 🎉 Final Notes

Keep it **SIMPLE**! The goal is a clean, fast-loading landing page that:
1. Showcases the API beautifully
2. Provides clear documentation
3. Offers working examples
4. Drives users to the API docs

**Remember**: When users click "Get API", they should go to `https://kalori-makanan-kkm.onrender.com/docs` for the full interactive documentation.

Focus on **quality over quantity** - a few well-designed pages are better than many mediocre ones.