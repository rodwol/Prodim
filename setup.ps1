# Define folder structures
$frontendFolders = @("public", "src/components", "src/pages", "src/assets", "src/services", "src/styles")
$mobileFolders = @("assets", "src/screens", "src/components", "src/navigation", "src/services")
$backendFolder = "backend"

# Create frontend folders
foreach ($folder in $frontendFolders) {
    New-Item -ItemType Directory -Path "dementia-prevention-platform/frontend/$folder" -Force
}

# Create mobile folders
foreach ($folder in $mobileFolders) {
    New-Item -ItemType Directory -Path "dementia-prevention-platform/mobile/$folder" -Force
}

# Create backend folder
New-Item -ItemType Directory -Path "dementia-prevention-platform/$backendFolder" -Force

# Create necessary files
$files = @(
    "frontend/src/App.js",
    "frontend/src/index.js",
    "frontend/package.json",
    "frontend/.env",
    "mobile/src/App.js",
    "mobile/package.json",
    "README.md"
)

foreach ($file in $files) {
    New-Item -ItemType File -Path "dementia-prevention-platform/$file" -Force
}

Write-Output "Project structure created successfully!"