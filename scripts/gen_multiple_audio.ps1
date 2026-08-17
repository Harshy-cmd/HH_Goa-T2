Add-Type -AssemblyName System.Speech
$queries = @(
    "What is the definition of medicine?",
    "How does a vector database work?",
    "What is retrieval augmented generation?",
    "What is a computer network?",
    "What is machine learning?"
)

for ($i = 0; $i -lt $queries.Count; $i++) {
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $file = "d:\hhgoarag\spoken_query_$($i + 1).wav"
    $synth.SetOutputToWaveFile($file)
    $synth.Speak($queries[$i])
    $synth.Dispose()
    Write-Host "Generated $file : $($queries[$i])"
}
