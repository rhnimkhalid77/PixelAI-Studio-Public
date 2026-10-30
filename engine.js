'use strict';

/*
 * PixelAI Studio - Creative Engine 0.1
 * Deterministic prompt planning only. No media inference or remote API calls.
 */
(function(global){
  const STYLE_PRESETS = {
    'Cinematografico': {
      visual:'composizione cinematografica, profondità di campo naturale, color grading professionale',
      camera:'movimento camera fluido e controllato, inquadrature coerenti',
      light:'illuminazione motivata, contrasto morbido e dettagli preservati'
    },
    'Fantascienza': {
      visual:'design futuristico credibile, dettagli tecnologici, atmosfera immersiva',
      camera:'movimento camera lento e dinamico, scala visiva leggibile',
      light:'luci volumetriche, riflessi controllati, palette luminosa coerente'
    },
    'Fantasy': {
      visual:'mondo fantastico ricco di dettagli, materiali e ambienti credibili',
      camera:'movimento di camera elegante, rivelazione graduale della scena',
      light:'luce atmosferica, bagliori delicati, ombre profonde ma leggibili'
    },
    'Animazione': {
      visual:'animazione curata, forme leggibili, movimento espressivo e coerente',
      camera:'camera stabile con movimenti morbidi e intenzionali',
      light:'illuminazione uniforme e palette cromatica armoniosa'
    },
    'Realistico': {
      visual:'resa fotorealistica, anatomia e proporzioni naturali, texture credibili',
      camera:'movimenti realistici, prospettiva naturale, nessuna distorsione',
      light:'luce naturale, esposizione bilanciata, ombre fisicamente plausibili'
    }
  };

  function cleanText(value, max){
    return String(value || '').replace(/[\u0000-\u001f\u007f]/g,' ').replace(/\s+/g,' ').trim().slice(0,max);
  }

  function buildPrompt(input){
    const scene = cleanText(input && input.scene,500);
    if(!scene) throw new Error('Scene description required');
    const style = STYLE_PRESETS[input.style] ? input.style : 'Cinematografico';
    const preset = STYLE_PRESETS[style];
    const output = input.output === 'image' ? 'image' : 'video';
    const language = input.language === 'en' ? 'en' : 'it';
    const prompt = [
      'SCENA: ' + scene,
      'STILE: ' + style + '; ' + preset.visual,
      'CAMERA: ' + preset.camera,
      'ILLUMINAZIONE: ' + preset.light,
      'CONTINUITÀ: mantieni costanti soggetti, abiti, oggetti, ambiente e direzione della luce tra le inquadrature.',
      'QUALITÀ: dettagli nitidi, composizione leggibile, movimento naturale, nessun artefatto visivo.'
    ].join('\n');
    const shots = output === 'video' ? [
      {id:1,durationSeconds:3,shot:'Campo medio di apertura',direction:'Presenta ambiente e soggetto, camera stabile.'},
      {id:2,durationSeconds:4,shot:'Inquadratura principale',direction:'Mostra l’azione centrale con movimento camera morbido.'},
      {id:3,durationSeconds:3,shot:'Dettaglio conclusivo',direction:'Chiudi con un dettaglio significativo e una transizione pulita.'}
    ] : [
      {id:1,shot:'Inquadratura principale',direction:'Composizione chiara con soggetto ben leggibile.'}
    ];
    return {
      engine:'PixelAI Creative Engine',
      engineVersion:'0.1.0',
      projectVersion:'0.8',
      createdAt:new Date().toISOString(),
      status:'prompt-ready-not-generated',
      output,
      language,
      style,
      sourceScene:scene,
      prompt,
      negativePrompt:'sfocatura involontaria, artefatti, anatomia deformata, dita extra, testo casuale, watermark, flicker, cambi improvvisi di identità o abbigliamento',
      shotPlan:shots,
      generation:{available:false,reason:'Manca ancora un modello generativo e un servizio di inferenza.'}
    };
  }

  function formatPreview(project){
    return 'MOTORE: ' + project.engine + ' v' + project.engineVersion +
      '\nSTATO: brief pronto · media non generato' +
      '\n\n' + project.prompt +
      '\n\nPIANO INQUADRATURE:\n' +
      project.shotPlan.map(s => s.id + '. ' + s.shot + ' (' + (s.durationSeconds || 0) + 's) — ' + s.direction).join('\n') +
      '\n\nVINCOLI NEGATIVI:\n' + project.negativePrompt;
  }

  global.PixelAIEngine = Object.freeze({buildPrompt,formatPreview});
})(window);
