import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import {
  Sun,
  Moon,
  Zap,
  Database,
  Search,
  ExternalLink,
  Code,
  Sparkles,
  ChefHat,
  BookOpen,
  Activity,
  Github,
  Play,
  Copy,
  Check
} from 'lucide-react'

// Types
interface Food {
  id: number
  name: string
  serving?: string
  weight_g?: number
  calories_kcal?: number
  category?: string
  reference?: string
}

interface SearchResponse {
  total: number
  foods: Food[]
}

interface Category {
  id: number
  name: string
}

interface HealthResponse {
  status: string
  message: string
  database_connected: boolean
}

// API functions
const API_BASE = ''

const fetchHealth = async (): Promise<HealthResponse> => {
  const response = await fetch(`${API_BASE}/health`)
  if (!response.ok) throw new Error('Failed to fetch health')
  return response.json()
}

const fetchCategories = async (): Promise<Category[]> => {
  const response = await fetch(`${API_BASE}/categories`)
  if (!response.ok) throw new Error('Failed to fetch categories')
  return response.json()
}

const searchFood = async (query: string): Promise<SearchResponse> => {
  const response = await fetch(`${API_BASE}/foods/search?name=${encodeURIComponent(query)}`)
  if (!response.ok) throw new Error('Failed to search food')
  return response.json()
}

// Dark mode hook
function useDarkMode() {
  const [isDark, setIsDark] = useState(() => {
    return localStorage.getItem('theme') === 'dark' ||
           (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)
  })

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }, [isDark])

  return [isDark, setIsDark] as const
}

// Copy to clipboard hook
function useCopyToClipboard() {
  const [copied, setCopied] = useState(false)

  const copy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  return { copied, copy }
}

// Components
function ThemeToggle({ isDark, toggleTheme }: { isDark: boolean; toggleTheme: () => void }) {
  return (
    <motion.button
      onClick={toggleTheme}
      className="glass-button p-3 text-white hover:text-yellow-300 transition-colors"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-label="Toggle theme"
    >
      <AnimatePresence mode="wait">
        {isDark ? (
          <motion.div
            key="sun"
            initial={{ rotate: -90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: 90, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Sun className="w-5 h-5" />
          </motion.div>
        ) : (
          <motion.div
            key="moon"
            initial={{ rotate: 90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: -90, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Moon className="w-5 h-5" />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  )
}

function StatusIndicator({ isOnline }: { isOnline: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <motion.div
        className={`w-3 h-3 rounded-full ${isOnline ? 'bg-green-400' : 'bg-red-400'}`}
        animate={isOnline ? { scale: [1, 1.2, 1] } : {}}
        transition={{ duration: 2, repeat: Infinity }}
      />
      <span className={`text-sm font-medium ${isOnline ? 'text-green-400' : 'text-red-400'}`}>
        {isOnline ? 'Online' : 'Offline'}
      </span>
    </div>
  )
}

function StatCard({ icon: Icon, number, label, delay = 0 }: {
  icon: React.ComponentType<any>
  number: string | number
  label: string
  delay?: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.6 }}
      className="stat-card hover:scale-105 transition-transform duration-300"
    >
      <Icon className="w-8 h-8 text-primary-400 mx-auto mb-3" />
      <div className="stat-number">{number}</div>
      <div className="stat-label">{label}</div>
    </motion.div>
  )
}

function CodeBlock({ code, language = 'bash' }: { code: string; language?: string }) {
  const { copied, copy } = useCopyToClipboard()

  return (
    <div className="relative">
      <div className="api-block">
        <div className="flex items-center justify-between mb-3">
          <span className="text-slate-400 text-xs uppercase tracking-wide">{language}</span>
          <button
            onClick={() => copy(code)}
            className="text-slate-400 hover:text-white transition-colors p-1 rounded"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
        <pre className="text-sm overflow-x-auto">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  )
}

function ApiExample({ title, description, endpoint, example }: {
  title: string
  description: string
  endpoint: string
  example: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="glass-card-hover p-6"
    >
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-white/70 mb-4">{description}</p>

      <a
        href={endpoint}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-2 text-primary-300 hover:text-primary-200 transition-colors mb-4"
      >
        <Play className="w-4 h-4" />
        Try it live
        <ExternalLink className="w-4 h-4" />
      </a>

      <CodeBlock code={example} />
    </motion.div>
  )
}

function SearchDemo() {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query)
    }, 500)

    return () => clearTimeout(timer)
  }, [query])

  const { data: searchResults, isLoading } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: () => searchFood(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
  })

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      className="glass-card p-6"
    >
      <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
        <Search className="w-6 h-6 text-primary-400" />
        Try the API Live
      </h3>

      <div className="relative mb-6">
        <input
          type="text"
          placeholder="Search for foods... (e.g., nasi lemak, rendang)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="glass-input text-white placeholder-white/50"
        />
        {isLoading && (
          <div className="absolute right-3 top-3">
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          </div>
        )}
      </div>

      <AnimatePresence>
        {searchResults && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-3"
          >
            <div className="text-white/70 text-sm">
              Found {searchResults.total} results
            </div>

            {searchResults.foods.slice(0, 3).map((food, index) => (
              <motion.div
                key={food.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass-card p-4 border-l-4 border-primary-400"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-semibold text-white">{food.name}</h4>
                    <p className="text-white/60 text-sm">{food.serving}</p>
                    {food.category && (
                      <span className="inline-block mt-1 px-2 py-1 bg-primary-500/20 text-primary-300 text-xs rounded">
                        {food.category}
                      </span>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold text-primary-300">
                      {food.calories_kcal || 'N/A'}
                    </div>
                    <div className="text-white/60 text-sm">kcal</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Main App Component
export default function App() {
  const [isDark, setIsDark] = useDarkMode()

  // Queries
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: fetchCategories,
  })

  // Sample search for stats
  const { data: statsSearch } = useQuery({
    queryKey: ['stats'],
    queryFn: () => searchFood('nasi'),
  })

  const isOnline = health?.database_connected ?? false
  const totalCategories = categories?.length ?? 0
  const estimatedFoods = statsSearch?.total ? Math.round(statsSearch.total * 15) : 750

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="glass-nav fixed top-0 left-0 right-0 z-50">
        <div className="container-custom py-4">
          <div className="flex items-center justify-between">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3"
            >
              <ChefHat className="w-8 h-8 text-primary-400" />
              <span className="text-xl font-bold text-white">Kalori Makanan API</span>
            </motion.div>

            <div className="flex items-center gap-4">
              <StatusIndicator isOnline={isOnline} />
              <ThemeToggle isDark={isDark} toggleTheme={() => setIsDark(!isDark)} />
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-flex items-center gap-2 glass-card px-4 py-2 mb-6"
            >
              <Sparkles className="w-4 h-4 text-yellow-400" />
              <span className="text-white/80 text-sm">Modern API for Food Calories</span>
            </motion.div>

            <h1 className="gradient-text mb-6 font-bold text-balance">
              🍽️ Kalori Makanan API
            </h1>

            <p className="text-xl text-white/80 mb-8 max-w-2xl mx-auto text-pretty">
              Fast & reliable food calorie lookup for Malaysian and international cuisine.
              Perfect for nutrition apps, meal planners, and health applications.
            </p>

            <div className="flex flex-wrap gap-4 justify-center">
              <a href="/docs" className="btn-primary flex items-center gap-2">
                <BookOpen className="w-5 h-5" />
                API Documentation
              </a>
              <a href="https://github.com/Zen0space/kalori-makanan-kkm" className="btn-secondary flex items-center gap-2">
                <Github className="w-5 h-5" />
                View Source
              </a>
            </div>
          </motion.div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
            <StatCard
              icon={Database}
              number={`${estimatedFoods}+`}
              label="Food Items"
              delay={0.2}
            />
            <StatCard
              icon={Activity}
              number={totalCategories}
              label="Categories"
              delay={0.4}
            />
            <StatCard
              icon={Zap}
              number="REST"
              label="API Standard"
              delay={0.6}
            />
          </div>
        </div>
      </section>

      {/* Live Demo Section */}
      <section className="py-20">
        <div className="container-custom">
          <SearchDemo />
        </div>
      </section>

      {/* API Examples Section */}
      <section className="py-20">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h2 className="gradient-text mb-4">Quick Start Examples</h2>
            <p className="text-white/70 text-lg">Try these endpoints right now</p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <ApiExample
              title="🔍 Search Foods"
              description="Find calorie information by food name"
              endpoint="/foods/search?name=nasi%20lemak"
              example='curl "https://kalori-makanan-kkm.onrender.com/foods/search?name=nasi%20lemak"'
            />

            <ApiExample
              title="📊 Browse Categories"
              description="Explore available food categories"
              endpoint="/categories"
              example='curl "https://kalori-makanan-kkm.onrender.com/categories"'
            />

            <ApiExample
              title="📋 List Foods"
              description="Browse paginated food database"
              endpoint="/foods?page=1&per_page=10"
              example='curl "https://kalori-makanan-kkm.onrender.com/foods?page=1&per_page=10"'
            />

            <ApiExample
              title="🎯 Get Specific Food"
              description="Retrieve detailed food information"
              endpoint="/foods/1"
              example='curl "https://kalori-makanan-kkm.onrender.com/foods/1"'
            />
          </div>
        </div>
      </section>

      {/* Integration Examples */}
      <section className="py-20">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h2 className="gradient-text mb-4">Easy Integration</h2>
            <p className="text-white/70 text-lg">Works with any programming language</p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="glass-card p-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Code className="w-5 h-5 text-yellow-400" />
                JavaScript
              </h3>
              <CodeBlock
                code={`fetch('/foods/search?name=nasi%20lemak')
  .then(res => res.json())
  .then(data => console.log(data))`}
                language="javascript"
              />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="glass-card p-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Code className="w-5 h-5 text-blue-400" />
                Python
              </h3>
              <CodeBlock
                code={`import requests
r = requests.get('/foods/search?name=nasi%20lemak')
data = r.json()`}
                language="python"
              />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 }}
              className="glass-card p-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Code className="w-5 h-5 text-green-400" />
                cURL
              </h3>
              <CodeBlock
                code={`curl "https://kalori-makanan-kkm.onrender.com/foods/search?name=nasi%20lemak"`}
                language="bash"
              />
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="glass-card p-8 text-center"
          >
            <h2 className="gradient-text mb-6">Perfect For</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 text-white/80">
              <div>📱 Nutrition Apps</div>
              <div>⚖️ Calorie Trackers</div>
              <div>🍽️ Meal Planners</div>
              <div>🏥 Health Applications</div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 text-center text-white/60">
        <div className="container-custom">
          <p>Made with ❤️ for the Malaysian food community | Powered by FastAPI & Turso</p>
        </div>
      </footer>
    </div>
  )
}
