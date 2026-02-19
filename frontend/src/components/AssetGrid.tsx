'use client'

import { Laptop, Monitor, Keyboard, Mouse, Headphones, Phone, Key, Package } from 'lucide-react'
import { AssetCard } from './AssetCard'

const categoryIcons: Record<string, any> = {
  laptop: Laptop,
  monitor: Monitor,
  keyboard: Keyboard,
  mouse: Mouse,
  headset: Headphones,
  phone: Phone,
  key: Key,
  license: Package,
  other: Package,
}

interface Asset {
  id: number
  asset_tag: string
  name: string
  category: string
  status: string
  manufacturer?: string
  model?: string
  location?: string
  assignee?: {
    full_name: string
    department: string
  }
}

interface AssetGridProps {
  assets: Asset[]
  loading: boolean
}

export function AssetGrid({ assets, loading }: AssetGridProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg p-4 animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        ))}
      </div>
    )
  }

  if (!assets || assets.length === 0) {
    return (
      <div className="text-center py-12">
        <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">No assets found</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {assets.map((asset) => (
        <AssetCard key={asset.id} asset={asset} Icon={categoryIcons[asset.category] || Package} />
      ))}
    </div>
  )
}
