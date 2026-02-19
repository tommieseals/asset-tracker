'use client'

import { Package, CheckCircle, Clock, AlertTriangle } from 'lucide-react'

interface StatsCardsProps {
  data?: {
    total_assets: number
    available_assets: number
    checked_out_assets: number
    maintenance_assets: number
    retired_assets: number
  }
  loading: boolean
}

export function StatsCards({ data, loading }: StatsCardsProps) {
  const stats = [
    { label: 'Total Assets', value: data?.total_assets || 0, icon: Package, color: 'bg-blue-500' },
    { label: 'Available', value: data?.available_assets || 0, icon: CheckCircle, color: 'bg-green-500' },
    { label: 'Checked Out', value: data?.checked_out_assets || 0, icon: Clock, color: 'bg-yellow-500' },
    { label: 'In Maintenance', value: data?.maintenance_assets || 0, icon: AlertTriangle, color: 'bg-red-500' },
  ]

  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg p-4 animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div key={stat.label} className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 ${stat.color} rounded-lg flex items-center justify-center`}>
              <stat.icon className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              <p className="text-sm text-gray-500">{stat.label}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
