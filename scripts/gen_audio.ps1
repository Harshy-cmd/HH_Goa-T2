Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile('d:\hhgoarag\spoken_query.wav')
$synth.Speak('What is the definition of medicine?')
$synth.Dispose()
Write-Host "Generated spoken_query.wav successfully."
