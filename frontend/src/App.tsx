// frontend/src/App.tsx

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

  useEffect(() => {
    fetch("/models/", { headers: { "x-api-key": "dev-key-123" } })
      .then((res) => res.json())
      .then((data) => {
        console.log("📦 Models fetched:", data)
        setModels(data.models || [])
        if (data.models?.length > 0) setModel(data.models[0])
      })
      .catch((err) => console.error("Failed to load models:", err))
  }, [])

  async function handleGenerate() {
    if (!model || !prompt.trim()) return
    setLoading(true)
    setOutput("")
  
    try {
      const res = await fetch("/generate/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": "dev-key-123",
        },
        body: JSON.stringify({ model, prompt, max_tokens: maxTokens }),
      })
  
      // ✅ Check for streaming NDJSON
      const contentType = res.headers.get("content-type") || ""
      if (contentType.includes("application/x-ndjson")) {
        const reader = res.body?.getReader()
        if (!reader) throw new Error("No stream reader available")
  
        let text = ""
        const decoder = new TextDecoder()
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          const chunk = decoder.decode(value, { stream: true }).trim()
          // some lines might be NDJSON, parse carefully
          for (const line of chunk.split("\n")) {
            if (!line.trim()) continue
            try {
              const json = JSON.parse(line)
              if (json.response) text += json.response
              else if (json.message?.content) text += json.message.content
            } catch {
              text += line
            }
          }
          setOutput(text)
        }
      } else {
        // ✅ Non-stream response (normal JSON)
        const data = await res.json()
        console.log("🧾 Full response:", data)
  
        // handle various formats gracefully
        if (typeof data === "string") setOutput(data)
        else if (data.response) setOutput(data.response)
        else if (data.generated_text) setOutput(data.generated_text)
        else if (data.choices?.[0]?.message?.content)
          setOutput(data.choices[0].message.content)
        else setOutput(JSON.stringify(data, null, 2))
      }
    } catch (err) {
      console.error("❌ Error generating:", err)
      setOutput("Error generating text.")
    } finally {
      setLoading(false)
    }
  }
  

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
      <div className="w-full max-w-2xl space-y-6">
        <h1 className="text-3xl font-bold text-center">🚀 Prodify Text Model Inference</h1>
        <p className="text-center text-gray-600">
          Generate text using local or hosted AI models.
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
            max={200}
            step={10}
          />
        </div>

        {/* Generate Button */}
        <div className="flex justify-center">
          <Button onClick={handleGenerate} disabled={loading || !model}>
            {loading ? "Generating..." : "Generate"}
          </Button>
        </div>

        {/* Output Card */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Output</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="whitespace-pre-wrap text-sm">{output || "No output yet."}</pre>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App