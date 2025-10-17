import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"

function App() {
  const [models, setModels] = useState<string[]>([])
  const [model, setModel] = useState("")
  const [prompt, setPrompt] = useState("Once upon a time in Bangalore,")
  const [maxTokens, setMaxTokens] = useState(200)
  const [loading, setLoading] = useState(false)
  const [output, setOutput] = useState("")
  const [jobId, setJobId] = useState<string | null>(null)
  const [status, setStatus] = useState("idle")

  useEffect(() => {
    fetch("/models")
      .then((res) => res.json())
      .then((data) => {
        setModels(data.models || [])
        if (data.models?.length > 0) setModel(data.models[0])
      })
      .catch((err) => console.error("Failed to load models:", err))
  }, [])

  async function handleGenerate() {
    if (!model || !prompt.trim()) return
    setLoading(true)
    setOutput("")
    setJobId(null)
    setStatus("queued")

    try {
      const res = await fetch("/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": "dev-key-123",
        },
        body: JSON.stringify({ model, prompt, max_tokens: maxTokens }),
      })

      const data = await res.json()
      if (data.job_id) {
        setJobId(data.job_id)
        pollStatus(data.job_id)
      } else {
        setOutput("Unexpected response: " + JSON.stringify(data))
        setLoading(false)
      }
    } catch (err) {
      console.error(err)
      setOutput("Error generating text.")
      setLoading(false)
    }
  }

  async function pollStatus(jobId: string) {
    const interval = setInterval(async () => {
      const res = await fetch(`/status/${jobId}`)
      const data = await res.json()

      if (data.status === "completed") {
        clearInterval(interval)
        setOutput(data.result.text || "No text returned.")
        setStatus("completed")
        setLoading(false)
      } else if (data.status === "failed") {
        clearInterval(interval)
        setOutput(`❌ Failed: ${data.error}`)
        setStatus("failed")
        setLoading(false)
      } else {
        setStatus(data.status)
      }
    }, 2000)
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
      <div className="w-full max-w-2xl space-y-6">
        <h1 className="text-3xl font-bold text-center">🚀 Prodify Text Inference Queue</h1>
        <p className="text-center text-gray-600">
          Generate text asynchronously via FastAPI + Celery + Ollama.
        </p>

        {/* Model Selector */}
        <div className="space-y-2">
          <Label>Select Model</Label>
          <Select value={model} onValueChange={setModel}>
            <SelectTrigger>
              <SelectValue placeholder="Choose a model..." />
            </SelectTrigger>
            <SelectContent>
              {models.map((m) => (
                <SelectItem key={m} value={m}>
                  {m}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Prompt Input */}
        <div className="space-y-2">
          <Label>Prompt</Label>
          <Textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your text prompt..."
            rows={5}
          />
        </div>

        {/* Token Slider */}
        <div className="space-y-2">
          <Label>Max Tokens: {maxTokens}</Label>
          <Slider
            value={[maxTokens]}
            onValueChange={(val) => setMaxTokens(val[0])}
            min={10}
            max={500}
            step={10}
          />
        </div>

        {/* Generate Button */}
        <div className="flex justify-center">
          <Button onClick={handleGenerate} disabled={loading || !model}>
            {loading ? `Generating (${status})...` : "Generate"}
          </Button>
        </div>

        {/* Output Card */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Output</CardTitle>
          </CardHeader>
          <CardContent>
            {jobId && (
              <div className="text-xs text-gray-500 mb-2">
                Job ID: <code>{jobId}</code> ({status})
              </div>
            )}
            <pre className="whitespace-pre-wrap text-sm">
              {output || "No output yet."}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App
