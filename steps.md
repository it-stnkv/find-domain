CLI контейнер   
[HOST FS]   
   ↓ (volume)   
[/data/domains.csv] → [CONTAINER] → [/data/results.csv]   
```
docker run --rm \   
  -v $(pwd)/data:/data \   
  domain-checker   
```

Контейнер = просто запуск твоего скрипта   
Как работает:   
1. пользователь монтирует папку   
2. кладёт туда domains.csv   
3. запускает контейнер   
4. получает results.csv    
Это обязательный базовый вариант, даже если будет UI   

---

CLI + аргументы   
можно использовать в пайплайнах   
--input /data/in.csv   
--output /data/out.csv   
```
docker run ... domain-checker \      
  --input /data/domains.csv \      
  --output /data/results.csv      
```

---

Web UI    

Browser → FastAPI → Worker → whois → result

Функционал:   
1. upload CSV    
2. запуск проверки    
3. статус     
4. скачать результат     
Компоненты:     
1. API слой:     
FastAPI      
2. Worker:    
ThreadPoolExecutor (как сейчас)    
ИЛИ     
Celery (если “по-взрослому”)      
3. Storage:     
временные файлы (/tmp или volume)     
🌐 UX:     
Страница:     
[Upload CSV]     
[Run]     
[Download result]

---

