'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { QrCode, ArrowRightLeft, User } from 'lucide-react'

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

const statusColors: Record<string, string> = {
  available: 'bg-green-100 text-green-800',
  checked_out: 'bg-blue-100 text-blue-800',
  maintenance: 'bg-yellow-100 text-yellow-800',
  retired: 'bg-gray-100 text-gray-800',
}

export function AssetCard({ asset, Icon }: { asset: Asset; Icon: any }) {
  const [showQR, setShowQR] = useState(false)
  const queryClient = useQueryClient()

  const checkinMutation = useMutation({
    mutationFn: () => api.post(`/api/assets/${asset.id}/checkin`, { notes: 'Quick check-in' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['assets'] }),
  })

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
            <Icon className="w-5 h-5 text-gray-600" />
          </div>
          <div>
            <h3 className="font-medium text-gray-900">{asset.name}</h3>
            <p className="text-sm text-gray-500">{asset.asset_tag}</p>
          </div>
        </div>
        <span className={`px-2 py-1 text-xs font-medium rounded ${statusColors[asset.status]}`}>
          {asset.status.replace('_', ' ')}
        </span>
      </div>

      <div className="text-sm text-gray-600 space-y-1 mb-4">
        {asset.manufacturer && asset.model && (
          <p>{asset.manufacturer} {asset.model}</p>
        )}
        {asset.location && <p>📍 {asset.location}</p>}
        {asset.assignee && (
          <p className="flex items-center gap-1">
            <User className="w-3 h-3" />
            {asset.assignee.full_name} ({asset.assignee.department})
          </p>
        )}
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => setShowQR(!showQR)}
          className="flex-1 px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 flex items-center justify-center gap-1"
        >
          <QrCode className="w-4 h-4" />
          QR Code
        </button>
        
        {asset.status === 'checked_out' && (
          <button
            onClick={() => checkinMutation.mutate()}
            disabled={checkinMutation.isPending}
            className="flex-1 px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-1"
          >
            <ArrowRightLeft className="w-4 h-4" />
            Check In
          </button>
        )}
        
        {asset.status === 'available' && (
          <a
            href={`/assets/${asset.id}/checkout`}
            className="flex-1 px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700 flex items-center justify-center gap-1"
          >
            <ArrowRightLeft className="w-4 h-4" />
            Check Out
          </a>
        )}
      </div>

      {showQR && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg text-center">
          <img
            src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/qr/${asset.id}`}
            alt={`QR Code for ${asset.asset_tag}`}
            className="mx-auto w-32 h-32"
          />
          <p className="text-xs text-gray-500 mt-2">{asset.asset_tag}</p>
        </div>
      )}
    </div>
  )
}
