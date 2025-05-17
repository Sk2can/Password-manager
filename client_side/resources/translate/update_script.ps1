# Путь к папке проекта (укажи свой)
$projectPath = "D:\khmel\Work\Diplom\Password_manager\client_side"

# Путь к ts-файлу
$tsFile = "$projectPath\client_side\resources\translate\ru_RU.ts"

# Переход в папку проекта
Set-Location $projectPath

# Собираем все .py и .ui файлы
$files = Get-ChildItem -Path $projectPath -Recurse -Include *.py, *.ui -File | ForEach-Object { $_.FullName }

# Проверяем, нашлись ли файлы
if ($files.Count -eq 0) {
    Write-Host "❌ Файлы не найдены. Проверь путь: $projectPath"
    exit
}

# Выводим список файлов
Write-Host "Файлы для перевода:"
$files | ForEach-Object { Write-Host $_ }

# Запускаем pylupdate5 с файлами
pylupdate5 @files -ts "D:\khmel\Work\Diplom\Password_manager\client_side\resources\translate\ru_RU.ts"