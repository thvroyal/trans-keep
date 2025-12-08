import { useParams } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Download, Link2, Link2Off } from 'lucide-react'
import { useReviewSync } from '@/hooks/useAppStore'

export default function ReviewPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const { syncEnabled, toggleSync } = useReviewSync()

  const handleDownload = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`/api/v1/download/${jobId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        window.open(data.download_url, '_blank')
      }
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-card">
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-foreground">document.pdf</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSync}
            className="gap-2"
          >
            {syncEnabled ? (
              <>
                <Link2 className="w-4 h-4" />
                <span className="hidden md:inline">Sync</span>
              </>
            ) : (
              <>
                <Link2Off className="w-4 h-4" />
                <span className="hidden md:inline">Sync Off</span>
              </>
            )}
          </Button>
        </div>
        <Button onClick={handleDownload} className="gap-2">
          <Download className="w-4 h-4" />
          Download PDF
        </Button>
      </div>

      <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-0">
        <div className="border-r border-border">
          <div className="sticky top-0 px-4 py-2 bg-muted/50 border-b border-border">
            <span className="text-sm font-medium text-muted-foreground">ORIGINAL</span>
          </div>
          <div className="p-8">
            <Card className="bg-card">
              <CardHeader>
                <CardTitle className="text-lg">Original Document</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  PDF viewer placeholder - Original document will be rendered here
                </p>
                <div className="mt-4 h-96 bg-muted rounded-lg flex items-center justify-center">
                  <span className="text-muted-foreground">PDF Preview Area</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <div>
          <div className="sticky top-0 px-4 py-2 bg-muted/50 border-b border-border">
            <span className="text-sm font-medium text-muted-foreground">TRANSLATED</span>
          </div>
          <div className="p-8">
            <Card className="bg-card">
              <CardHeader>
                <CardTitle className="text-lg">Translated Document</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  PDF viewer placeholder - Translated document will be rendered here
                </p>
                <div className="mt-4 h-96 bg-muted rounded-lg flex items-center justify-center">
                  <span className="text-muted-foreground">PDF Preview Area</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <div className="border-t border-border bg-card px-4 py-4">
        <div className="container max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-foreground">
              REFINE YOUR TRANSLATION
            </span>
          </div>
          <Separator className="mb-4" />
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm text-muted-foreground mr-2">Tone:</span>
            {['Formal', 'Casual', 'Creative', 'Technical', 'Academic'].map((tone) => (
              <Button key={tone} variant="outline" size="sm">
                {tone}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
