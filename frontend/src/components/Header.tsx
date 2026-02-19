'use client'

import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { LogOut, User, Settings, FileText } from 'lucide-react'

export function Header() {
  const router = useRouter()

  const { data: user } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => api.get('/api/users/me').then(res => res.data),
  })

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/')
  }

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">A</span>
          </div>
          <span className="text-xl font-bold text-gray-900">Asset Tracker</span>
        </div>

        <nav className="flex items-center gap-6">
          <a href="/dashboard" className="text-gray-600 hover:text-gray-900">
            Dashboard
          </a>
          <a href="/assets" className="text-gray-600 hover:text-gray-900">
            Assets
          </a>
          {user?.role === 'admin' && (
            <a href="/users" className="text-gray-600 hover:text-gray-900">
              Users
            </a>
          )}
          {(user?.role === 'admin' || user?.role === 'auditor') && (
            <a href="/audit" className="text-gray-600 hover:text-gray-900">
              Audit Log
            </a>
          )}
        </nav>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <User className="w-4 h-4" />
            <span>{user?.full_name || user?.username}</span>
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs capitalize">
              {user?.role}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            title="Logout"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  )
}
