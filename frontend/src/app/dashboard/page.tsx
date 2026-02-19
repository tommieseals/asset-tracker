'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Header } from '@/components/Header'
import { AssetGrid } from '@/components/AssetGrid'
import { SearchBar } from '@/components/SearchBar'
import { StatsCards } from '@/components/StatsCards'
import { Laptop, Monitor, Key, Headphones, Phone, Package } from 'lucide-react'

const categoryIcons: Record<string, any> = {
  laptop: Laptop,
  monitor: Monitor,
  key: Key,
  headset: Headphones,
  phone: Phone,
  other: Package,
}

export default function Dashboard() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/')
    }
  }, [router])

  const { data: dashboardData, isLoading: dashLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/api/assets/dashboard').then(res => res.data),
  })

  const { data: assets, isLoading: assetsLoading } = useQuery({
    queryKey: ['assets', selectedCategory],
    queryFn: () => {
      const params = new URLSearchParams()
      if (selectedCategory) params.set('category', selectedCategory)
      return api.get(`/api/assets/?${params}`).then(res => res.data)
    },
  })

  const { data: searchResults, isLoading: searchLoading } = useQuery({
    queryKey: ['search', searchQuery],
    queryFn: () => api.post('/api/search/ai', { query: searchQuery }).then(res => res.data),
    enabled: searchQuery.length > 2,
  })

  const displayAssets = searchQuery.length > 2 ? searchResults?.assets : assets

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Asset Dashboard</h1>
        
        {/* Stats Cards */}
        <StatsCards data={dashboardData} loading={dashLoading} />
        
        {/* Search */}
        <div className="my-6">
          <SearchBar 
            value={searchQuery} 
            onChange={setSearchQuery}
            placeholder="Search assets... Try: 'show me all laptops assigned to engineering'"
          />
        </div>

        {/* Category Filter */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              !selectedCategory ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            All
          </button>
          {['laptop', 'monitor', 'keyboard', 'mouse', 'headset', 'phone', 'license', 'key'].map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-lg text-sm font-medium capitalize ${
                selectedCategory === cat ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {cat}s
            </button>
          ))}
        </div>

        {/* Asset Grid */}
        <AssetGrid 
          assets={displayAssets || []} 
          loading={assetsLoading || searchLoading} 
        />
      </main>
    </div>
  )
}
