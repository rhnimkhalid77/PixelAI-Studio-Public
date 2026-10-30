# PixelAI Studio — public preview

> Copia pubblica sperimentale del progetto. Il repository originale `PixelAI-Studio` resta separato e privato. Questo prototipo non è pronto per uso commerciale o per la pubblicazione su App Store.

Prototipo web mobile-first in italiano, pensato per essere provato anche da iPhone.

## Funzioni della PWA
- Importa foto JPG, PNG e WebP (limite prototipo: 20 MB e 32 megapixel).
- Regola luminosità, contrasto e saturazione; ruota la foto e la esporta in PNG.
- Crea brief creativi strutturati con stile, indicazioni di camera e luce e piano di inquadrature.
- Salva fino a 20 progetti nel browser del dispositivo.
- Mostra il prezzo Premium previsto di 8,99 €/mese; pagamenti e abbonamenti non sono attivi.

## Stato del motore IA
- Il nucleo creativo nel browser genera prompt e piani di scena deterministici: non è un modello IA e non genera media.
- Il server separato `server/` contiene un'API FastAPI protetta da token e un adapter Diffusers per generare immagini con il modello predefinito SDXL Turbo.
- La generazione immagini lato server è implementata nel codice, ma non è ancora distribuita né collegata alla PWA. Per funzionare richiede dipendenze, download dei pesi, licenza del modello verificata e risorse di calcolo adeguate.
- La generazione video, il face swap, gli account, le quote per utente, la moderazione automatica e i pagamenti non sono implementati.
- PixelAI non ha ancora un modello proprietario addestrato da zero.

## Privacy
- La PWA attuale elabora le foto localmente nel browser e non le invia al server PixelAI.
- I progetti creati sono conservati nel localStorage del browser sul dispositivo.
- L'API server non salva intenzionalmente prompt o immagini generate, ma il provider di hosting e i suoi log devono essere verificati prima di un uso reale.
- `privacy.html` è una bozza: il titolare deve inserire i propri dati e verificare hosting, log, fornitori, basi giuridiche e tempi di conservazione.
- Non caricare immagini di altre persone senza averne titolo e autorizzazione.

## Avvio locale del server IA

Questa procedura richiede un computer/server, non può essere completata dal solo iPhone.

1. Installa Docker e Docker Compose sul server.
2. Entra nella cartella `server/`.
3. Copia `.env.example` in `.env`.
4. Genera un token segreto casuale di almeno 32 caratteri (per esempio `openssl rand -hex 32`) e inseriscilo in `.env`.
5. Verifica la licenza del modello SDXL Turbo e le condizioni d'uso prima di scaricare i pesi.
6. Esegui `docker compose -f compose.yaml up --build`. Il primo avvio scarica dipendenze e pesi e può richiedere molto spazio e tempo.
7. Verifica `http://127.0.0.1:8000/health`; la documentazione API è su `http://127.0.0.1:8000/docs`.

Il Dockerfile è una configurazione CPU generica: la generazione può essere molto lenta senza GPU. Per uso reale predisponi un host GPU e versioni CUDA/PyTorch compatibili. L'API è associata a localhost per impostazione predefinita: non esporla direttamente a Internet. Il token condiviso è una protezione minima e non sostituisce autenticazione per utente, rate limit, moderazione, logging controllato e gestione degli abusi. Le immagini sono restituite in base64 e non vengono salvate dal server.

## Come provare la PWA su iPhone
1. In GitHub apri **Settings → Pages**.
2. Seleziona **Deploy from a branch**, branch `main`, cartella `/(root)`, quindi salva.
3. Attendi che GitHub Pages confermi la pubblicazione e apri l'URL HTTPS indicato da GitHub in Safari.
4. In Safari usa **Condividi → Aggiungi alla schermata Home**.
5. Se compare una versione precedente, chiudi la web app, cancella i dati del sito in Safari e riaprila.

GitHub Pages non è ancora confermato come attivo per questo repository.

## Verifiche e lavori necessari prima del lancio
1. Provare l'editor, esportazione, installazione PWA e funzionamento offline su iPhone.
2. Distribuire e testare il server su hardware adeguato; verificare qualità, tempi e costi del modello.
3. Implementare autenticazione per utente, quote, rate limit e moderazione prima di esporre la generazione.
4. Collegare la PWA all'API solo dopo aver completato i controlli di sicurezza. Non inserire mai il token server nel codice client.
5. Valutare consenso, protezione dei dati e requisiti specifici prima di introdurre funzioni con volti o immagini caricate.
6. Implementare account e pagamenti solo dopo aver verificato la sostenibilità dei costi ricorrenti.
7. Preparare la pubblicazione App Store e completare la conformità legale e privacy.

## Sicurezza
- Non committare mai `.env`, token, chiavi API o password.
- La CSP e la Referrer-Policy attuali sono inserite come meta tag; non sostituiscono intestazioni HTTP configurate lato hosting.
- Completare i dati del titolare in `privacy.html` prima di una pubblicazione.
- Questo progetto è un prototipo sperimentale e non è pronto per la pubblicazione commerciale.
