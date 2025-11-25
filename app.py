from flask import Flask, render_template_string, request

app = Flask(__name__)

TEMPLATE = r"""
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Simulador Aposta de Valor</title>
  <style>
    :root{
      --bg:#0f172a;           /* azul bem escuro (slate-900) */
      --card:#111827;         /* quase preto (gray-900)       */
      --accent:#1e293b;       /* azul escuro (slate-800)      */
      --accent-2:#0b2c5a;     /* azul escuro para blocos      */
      --text:#e5e7eb;         /* texto claro                  */
      --muted:#94a3b8;        /* texto secundário             */
      --ok:#16a34a;           /* verde                        */
      --bad:#dc2626;          /* vermelho                     */
      --focus:#38bdf8;        /* azul claro foco              */
      --white:#ffffff;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";
      background:linear-gradient(120deg,#0b152a 0%, #0f172a 40%, #111827 100%);
      color:var(--text);
    }
    .container{
      max-width: 1050px;
      margin: 32px auto;
      padding: 0 16px;
    }
    .header{
      display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;
    }
    h1{font-size: clamp(22px, 3vw, 36px); margin:0;}
    .lang-switch button{
      border:1px solid #334155;
      background:transparent;
      color:var(--text);
      padding:8px 12px;
      border-radius:12px;
      cursor:pointer;
      margin-left:8px;
    }
    .lang-switch button.active{border-color:var(--focus); box-shadow:0 0 0 2px rgba(56,189,248,0.25) inset}
    .card{
      background:rgba(17,24,39,0.7);
      border:1px solid #1f2937;
      border-radius:16px;
      padding:16px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.20);
      backdrop-filter: blur(6px);
    }
    .row{
      display:grid;
      grid-template-columns: 1.2fr auto 1fr;
      gap:12px;
      align-items:center;
      margin-bottom:10px;
    }
    .row .label{
      background: var(--accent-2);
      color: var(--white);
      padding:12px 14px;
      border-radius:12px;
      font-weight:600;
      display:flex; align-items:center; justify-content:space-between;
    }
    .row .label .info{
      margin-left:12px;
      width:26px;height:26px;border-radius:50%;
      background: rgba(255,255,255,0.12);
      display:inline-flex;align-items:center;justify-content:center;
      cursor:pointer; border:none; color:white; font-weight:700;
    }
    input[type="number"], select, input[type="text"]{
      width:100%;
      padding:12px 14px;
      border-radius:12px;
      border:1px solid #334155;
      background:#0b1220;
      color:var(--text);
      outline:none;
    }
    input:focus, select:focus{border-color:var(--focus); box-shadow:0 0 0 3px rgba(56,189,248,0.15)}
    .grid{
      display:grid;
      grid-template-columns: 1fr 1fr;
      gap:16px;
    }
    .analysis{
      background: var(--accent);
      border-radius:14px;
      padding:14px;
      line-height:1.4;
      border:1px solid #334155;
    }
    .badge{
      display:inline-block;
      padding:6px 10px;
      border-radius:999px;
      font-weight:700;
    }
    .badge.ok{ background: rgba(22,163,74,0.2); color:#dcfce7; border:1px solid rgba(22,163,74,0.45)}
    .badge.bad{ background: rgba(220,38,38,0.2); color:#fee2e2; border:1px solid rgba(220,38,38,0.45)}
    .stakes{
      margin-top:12px;
      border-top:1px dashed #334155;
      padding-top:12px;
      font-variant-numeric: tabular-nums;
    }
    .stake-line{margin:6px 0}
    .muted{ color: var(--muted) }
    .footer-note{ margin-top:18px; font-size: 13px; color: var(--muted); }
    .controls{display:flex; gap:12px; align-items:center; margin-bottom:14px;}
    .popover{
      position: absolute;
      background:#020617;
      color:#e2e8f0;
      border:1px solid #334155;
      border-radius:12px;
      padding:10px 12px;
      font-size:14px;
      max-width: 280px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.35);
      z-index: 20;
      display:none;
    }
    .sr{ position:absolute !important; left:-9999px !important; }
    @media (max-width: 820px){
      .grid{ grid-template-columns: 1fr; }
      .row{ grid-template-columns: 1fr auto 1fr; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1 id="title">Simulador Aposta de Valor</h1>
      <div class="lang-switch">
        <span class="muted" id="langLabel">Idioma:</span>
        <button id="btnBR" class="active">BR</button>
        <button id="btnUS">US</button>
      </div>
    </div>

    <div class="card">
      <div class="controls">
        <label for="strategy" id="strategyLabel"><strong>Estratégia:</strong></label>
        <select id="strategy">
          <option value="duplo">Handcap M-Duplo</option>
          <option value="triplo">Handcap M-Triplo</option>
          <option value="quadruplo" selected>Handcap M-Quadruplo</option>
        </select>
        <div style="flex:1"></div>
        <label for="total" id="totalLabel"><strong>Total a Apostar</strong></label>
        <input id="total" type="number" step="0.01" value="100">
      </div>

      <div id="lines"></div>

      <div class="grid">
        <div class="analysis" id="analysisBox">
          <div><strong id="analysisTitle">Análise:</strong></div>
          <div id="analysisText" class="muted"></div>
          <div style="margin-top:8px">
            <span id="badge" class="badge bad">BetFail</span>
          </div>
        </div>

        <div class="analysis">
          <div><strong id="stakesTitle">Stakes & Retornos</strong></div>
          <div class="stakes" id="stakesList"></div>
        </div>
      </div>

      <div class="footer-note" id="tip">
        Dica: preencha as odds. Se a soma de (1/odd) dos mercados for menor que 1, há arbitragem (SureBet) e o retorno é igual em todos os cenários.
      </div>
    </div>
  </div>

  <!-- Popover (um só, reposicionado conforme o botão clicado) -->
  <div id="popover" class="popover" role="dialog" aria-modal="true"></div>

  <script>
    // ========= Traduções =========
    const T = {
      "pt": {
        title: "Simulador Aposta de Valor",
        langLabel: "Idioma:",
        strategy: "Estratégia:",
        strategies: {
          duplo: "Handcap M-Duplo",
          triplo: "Handcap M-Triplo",
          quadruplo: "Handcap M-Quadruplo",
        },
        total: "Total a Apostar",
        oddsPH: "ex.: 4.50",
        analysis: "Análise:",
        stakesTitle: "Stakes & Retornos",
        stakeLabel: (i, name, cur, stake, ret, frac, sum, tot) =>
          `Stake ${i}: ${name} ${stake} &nbsp;&nbsp; → retorna ${ret} &nbsp;&nbsp;`,
        surebet: (pct) => `SureBet — soma(S)=S<1.00. Payout alvo = Total/S. (S = {S}).`,
        betfail:  (S)  => `BetFail — soma(S) ≥ 1.00 (S = ${S}).`,
        badgeOK: "SureBet",
        badgeBAD:"BetFail - Não Aposte!",
        tip: "Dica: preencha as odds. Se a soma de (1/odd) dos mercados for menor que 1, há arbitragem (SureBet) e o retorno é igual em todos os cenários.",
        labels: {
          m1: "- 2 [Empate]",
          m2: "- 1 [Empate]",
          m3: "+ 1 [Empate]",
          m4: "Empate com gols",
        },
        infos: {
          m1: "Betano → Jogo → Handicap → Empate → - 2",
          m2: "Betano → Jogo → Handicap → Empate → - 1",
          m3: "Betano → Jogo → Handicap → Empate → + 1",
          m4: "Betano → Jogo → Especiais → Resultado Correto (Multiplica) → Empate com gols",
        },
        currency: "BRL",
        currencySymbol: "R$"
      },
      "en": {
        title: "Value Bet Simulator",
        langLabel: "Language:",
        strategy: "Strategy:",
        strategies: {
          duplo: "Handicap M-Double",
          triplo: "Handicap M-Triple",
          quadruplo: "Handicap M-Quadruple",
        },
        total: "Total to Stake",
        oddsPH: "e.g. 4.50",
        analysis: "Analysis:",
        stakesTitle: "Stakes & Returns",
        stakeLabel: (i, name, cur, stake, ret, frac, sum, tot) =>
          `Stake ${i}: ${name} ${cur} ${stake}  → returns ${cur} ${ret}`,
        surebet: (pct) => `SureBet — sum(S)=S<1.00. Target payout = Total/S. (S = {S}).`,
        betfail:  (S)  => `BetFail — sum(S) ≥ 1.00 (S = ${S}).`,
        badgeOK: "SureBet",
        badgeBAD:"BetFail - Do Not Bet!",
        tip: "Tip: fill the odds. If the sum of (1/odd) is less than 1, there is arbitrage (SureBet) and the payout equals across outcomes.",
        labels: {
          m1: "- 2 [Draw]",
          m2: "- 1 [Draw]",
          m3: "+ 1 [Draw]",
          m4: "Draw with goals",
        },
        infos: {
          m1: "Betano → Match → Handicap → Draw → - 2",
          m2: "Betano → Match → Handicap → Draw → - 1",
          m3: "Betano → Match → Handicap → Draw → + 1",
          m4: "Betano → Match → Specials → Correct Score (Multiples) → Draw with goals",
        },
        currency: "USD",
        currencySymbol: "$"
      }
    };

    // ========= Estado =========
    let LANG = "pt";

    const el = id => document.getElementById(id);
    const fmt = (value, currency) => {
      try{
        return new Intl.NumberFormat(LANG === "pt" ? "pt-BR" : "en-US",
          { style: "currency", currency: T[LANG].currency, minimumFractionDigits: 2 }).format(value);
      }catch(e){
        // fallback
        const sym = T[LANG].currencySymbol;
        return sym + " " + (Math.round(value*100)/100).toFixed(2);
      }
    };
    const num = v => {
      if(typeof v === "number") return v;
      if(!v) return NaN;
      // aceitar ponto ou vírgula
      const s = (""+v).replace(",", ".").replace(/[^0-9.\-]/g,"");
      return parseFloat(s);
    };

    // ========= UI build =========
    function buildLines(){
      const strategy = el("strategy").value;
      const linesWrap = el("lines");
      linesWrap.innerHTML = "";
      const itemsByStrategy = {
        "duplo":  ["m1","m2"],
        "triplo": ["m1","m2","m3"],
        "quadruplo": ["m1","m2","m3","m4"]
      };
      const keys = itemsByStrategy[strategy];

      keys.forEach((key, idx) => {
        const row = document.createElement("div");
        row.className = "row";
        const lab = document.createElement("div");
        lab.className = "label";
        lab.innerHTML = `<span>${T[LANG].labels[key]}</span>`;
        const infoBtn = document.createElement("button");
        infoBtn.className = "info";
        infoBtn.type = "button";
        infoBtn.textContent = "i";
        infoBtn.addEventListener("click", (e)=> showInfo(e, T[LANG].infos[key]));
        lab.appendChild(infoBtn);

        const x = document.createElement("div"); x.textContent = "→";
        x.className = "muted"; x.style.textAlign="center";

        const input = document.createElement("input");
        input.type = "number"; input.step = "0.01"; input.placeholder = T[LANG].oddsPH;
        input.id = "odd_"+key;
        input.addEventListener("input", recalc);

        row.appendChild(lab);
        row.appendChild(x);
        row.appendChild(input);
        linesWrap.appendChild(row);
      });

      recalc();
    }

    function setLanguage(lang){
      LANG = lang;
      // Toggle classes
      el("btnBR").classList.toggle("active", LANG==="pt");
      el("btnUS").classList.toggle("active", LANG==="en");

      // Textos
      el("title").textContent = T[LANG].title;
      el("langLabel").textContent = T[LANG].langLabel;
      el("strategyLabel").textContent = T[LANG].strategy;
      el("totalLabel").innerHTML = "<strong>"+T[LANG].total+"</strong>";
      // Repopular opções mantendo value
      const s = el("strategy"); const val = s.value;
      s.innerHTML = `
        <option value="duplo">${T[LANG].strategies.duplo}</option>
        <option value="triplo">${T[LANG].strategies.triplo}</option>
        <option value="quadruplo">${T[LANG].strategies.quadruplo}</option>`;
      s.value = val;

      el("analysisTitle").textContent = T[LANG].analysis;
      el("stakesTitle").textContent = T[LANG].stakesTitle;
      el("tip").textContent = T[LANG].tip;

      buildLines(); // reconstrói rótulos + recalc
    }

    // ========= Popover =========
    const pop = el("popover");
    function showInfo(ev, text){
      pop.textContent = text;
      pop.style.display = "block";
      const rect = ev.target.getBoundingClientRect();
      const top = window.scrollY + rect.top + rect.height + 8;
      const left = window.scrollX + rect.left - 8;
      pop.style.top = top + "px";
      pop.style.left = left + "px";
      // esconder ao clicar fora
      const hide = (e)=>{
        if(!pop.contains(e.target) && e.target !== ev.target){
          pop.style.display = "none";
          document.removeEventListener("click", hide);
        }
      };
      setTimeout(()=> document.addEventListener("click", hide), 0);
    }

    // ========= Cálculo =========
    function recalc(){
      const strategy = el("strategy").value;
      const itemsByStrategy = {
        "duplo":  ["m1","m2"],
        "triplo": ["m1","m2","m3"],
        "quadruplo": ["m1","m2","m3","m4"]
      };
      const keys = itemsByStrategy[strategy];

      const odds = [];
      for(const k of keys){
        const v = num( (el("odd_"+k)||{}).value );
        odds.push( isFinite(v) && v>0 ? v : NaN );
      }

      const total = num(el("total").value);
      const fs = odds.map(o => 1/(o||NaN));
      const S = fs.reduce((acc, f)=> acc + (isFinite(f)?f:0), 0);
      const Sdisp = (Math.round(S*1000)/1000).toFixed(3);

      const badge = el("badge");
      const analysisText = el("analysisText");

      if(odds.some(isNaN) || !isFinite(total) || total<=0){
        analysisText.textContent = LANG==="pt"
          ? "Preencha todas as odds e o Total para ver o resultado."
          : "Fill all odds and Total to see the result.";
        badge.textContent = T[LANG].badgeBAD;
        badge.className = "badge bad";
        el("stakesList").innerHTML = "";
        return;
      }

      const isSure = S < 1.0;
      if(isSure){
        badge.textContent = T[LANG].badgeOK;
        badge.className = "badge ok";
        analysisText.textContent = T[LANG].surebet().replace("{S}", Sdisp);
      }else{
        badge.textContent = T[LANG].badgeBAD;
        badge.className = "badge bad";
        analysisText.textContent = T[LANG].betfail(Sdisp);
      }

      // Payout alvo = Total / S (igual para todos)
      const target = total / S;
      const stakes = fs.map(f => (f / S) * total);

      // Render stakes
      const namesPT = [T[LANG].labels.m1, T[LANG].labels.m2, T[LANG].labels.m3, T[LANG].labels.m4];
      const currencySymbol = T[LANG].currencySymbol;
      let html = "";
      stakes.forEach((st, i)=>{
        const name = namesPT[i];
        const frac = (Math.round(fs[i]*1000)/1000).toFixed(3);
        html += `<div class="stake-line">` +
          `${T[LANG].stakeLabel(i+1, name, currencySymbol, 
             (fmt(st, T[LANG].currency)),
             (fmt(target, T[LANG].currency)),
             frac, "${Sdisp}", (fmt(total, T[LANG].currency))
          )}</div>`;
      });
      el("stakesList").innerHTML = html;
    }

    // ========= Eventos =========
    el("strategy").addEventListener("change", buildLines);
    el("total").addEventListener("input", recalc);
    el("btnBR").addEventListener("click", ()=> setLanguage("pt"));
    el("btnUS").addEventListener("click", ()=> setLanguage("en"));

    // Init
    setLanguage("pt");
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
