import { Outlet } from 'react-router-dom'
import { Toaster } from 'sonner'
import Header from './Header'

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <Toaster position="top-right" richColors />
    </div>
  )
}
