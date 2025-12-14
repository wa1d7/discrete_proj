## Загальна інформація

* Візуалізації результатів зберігаються у директорії `plots`.
* Числові результати експериментів зберігаються у директорії `results` у форматі CSV.

## Запуск прогону експериментів (PowerShell)

```powershell
cd path/to/project
python rabotaem.py --save-examples --example-every-k 5 --repeats 20 --ns 20,40,60,80,100,120,140,160,180,200 --densities 0.01,0.05,0.10,0.20,0.50
```

## Запуск без збереження візуалізації

```powershell
python rabotaem.py
```

## Зафорсити перезапис візуалізацій

```powershell
python rabotaem.py --save-examples --overwrite-visuals
```

