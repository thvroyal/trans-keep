import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'

export default function Header() {
  const { user, isAuthenticated, signIn, signOut } = useAuth()
  const navigate = useNavigate()

  const handleSignOut = async () => {
    await signOut()
    navigate('/')
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-card">
      <div className="container flex h-16 items-center justify-between px-4 md:px-8">
        <Link to="/" className="flex items-center gap-2">
          <span className="text-xl font-bold text-foreground">TransKeep</span>
        </Link>

        <nav className="flex items-center gap-4">
          {isAuthenticated ? (
            <>
              <div className="flex items-center gap-2">
                {user?.picture_url && (
                  <img
                    src={user.picture_url}
                    alt={user.name || 'User avatar'}
                    className="w-8 h-8 rounded-full"
                  />
                )}
                <span className="text-sm text-muted-foreground hidden md:inline">
                  {user?.name || user?.email}
                </span>
              </div>
              <Button variant="outline" size="sm" onClick={handleSignOut}>
                Sign Out
              </Button>
            </>
          ) : (
            <Button onClick={signIn}>Sign In with Google</Button>
          )}
        </nav>
      </div>
    </header>
  )
}
