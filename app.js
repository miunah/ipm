/* IPM Descomplicado — lógica da página (sem dependências, funciona via file://) */
(function () {
  "use strict";

  // Descrições curtas de cada conjunto (curadoria a partir do dataset)
  var DESCRICOES = {
    "Arrecadação": "Os tributos e receitas do município: IPTU, ISSQN, ITBI, taxas, tarifa de água, dívida ativa, certidões e parcelamentos.",
    "Recursos Humanos": "A vida funcional dos servidores: folha de pagamento, ponto eletrônico, férias, concursos públicos, treinamento e saúde ocupacional.",
    "Governo Digital": "Os canais entre a prefeitura e o cidadão: Portal do Cidadão, autoatendimento, ouvidoria, processo digital, transparência e diário oficial.",
    "Gerenciamento": "A administração do próprio sistema: usuários, permissões, logs, documentos, agendamento de tarefas e geração de relatórios personalizados.",
    "Cadastros Únicos": "O cadastro central de pessoas físicas e jurídicas da entidade, compartilhado por todos os outros conjuntos.",
    "Social": "A assistência social: programas e serviços à população, prontuário social e benefícios eventuais (como cesta básica).",
    "Vigilância em Saúde": "Vigilância sanitária, ambiental e epidemiológica: alvarás e licenças de funcionamento, fiscalização de estabelecimentos.",
    "Menu Inicial": "A tela de abertura do sistema, com indicadores e painéis de acompanhamento da gestão.",
    "Procuradoria": "A área jurídica: processos judiciais e administrativos, execuções fiscais, agenda de prazos e legislação.",
    "Fiscal": "As obrigações fiscais: escrita fiscal, Simples Nacional, nota fiscal eletrônica e fiscalização.",
    "Contabilidade": "Controle interno, planejamento e orçamento e execução orçamentária da entidade.",
    "Administração Geral": "Gestão ambiental (IPM Ambiental) e gerenciamento de documentos da administração.",
    "Área de Trabalho": "As preferências do usuário: barra de ferramentas, notificações, senha e personalização do ambiente.",
    "Suprimentos": "O suporte material: frota, compras e contratos, almoxarifado e patrimônio.",
    "Outros": "Conteúdos gerais, guias e perguntas frequentes sobre o sistema como um todo."
  };

  var ORDEM = ["Arrecadação", "Recursos Humanos", "Governo Digital", "Gerenciamento",
    "Cadastros Únicos", "Social", "Vigilância em Saúde", "Menu Inicial", "Procuradoria",
    "Fiscal", "Contabilidade", "Administração Geral", "Área de Trabalho", "Suprimentos", "Outros"];

  function semAcento(s) {
    return s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  }

  function el(tag, classe, texto) {
    var e = document.createElement(tag);
    if (classe) e.className = classe;
    if (texto != null) e.textContent = texto;
    return e;
  }

  // ---------- estatísticas do hero ----------
  document.getElementById("stat-rotinas").textContent = DADOS.total.toLocaleString("pt-BR");
  var nModulos = ORDEM.filter(function (m) { return DADOS.modulos[m]; }).length;
  document.getElementById("stat-modulos").textContent = nModulos;
  document.getElementById("stat-conceitos").textContent = document.querySelectorAll(".card.termo").length;

  // ---------- cards de conjuntos ----------
  var grade = document.getElementById("grade-modulos");
  ORDEM.forEach(function (nome) {
    var info = DADOS.modulos[nome];
    if (!info) return;
    var card = el("div", "card");
    var h = el("h4", null, nome);
    var badge = el("span", "badge-n", info.n + " rotinas");
    h.appendChild(badge);
    card.appendChild(h);
    card.appendChild(el("p", null, DESCRICOES[nome] || ""));
    if (info.areas && info.areas.length) {
      var lista = el("div", "areas-lista");
      info.areas.slice(0, 6).forEach(function (a) {
        lista.appendChild(el("span", null, a));
      });
      card.appendChild(lista);
    }
    grade.appendChild(card);
  });

  // ---------- busca ----------
  var campo = document.getElementById("campo-busca");
  var filtro = document.getElementById("filtro-modulo");
  var contador = document.getElementById("contador");
  var listaEl = document.getElementById("resultados");
  var LIMITE = 60;

  ORDEM.forEach(function (nome) {
    if (!DADOS.modulos[nome]) return;
    var op = el("option", null, nome + " (" + DADOS.modulos[nome].n + ")");
    op.value = nome;
    filtro.appendChild(op);
  });

  // índice de busca pré-computado (sem acentos)
  var indice = DADOS.rotinas.map(function (r) {
    return { r: r, chave: semAcento(r.t + " " + r.c + " " + r.d) };
  });

  function buscar() {
    var termo = semAcento(campo.value.trim());
    var mod = filtro.value;
    listaEl.innerHTML = "";

    if (termo.length < 2 && !mod) {
      contador.textContent = "Digite pelo menos 2 letras ou escolha um conjunto para listar as rotinas.";
      return;
    }

    var achados = [];
    for (var i = 0; i < indice.length; i++) {
      var item = indice[i];
      if (mod && item.r.m !== mod) continue;
      if (termo.length >= 2 && item.chave.indexOf(termo) === -1) continue;
      achados.push(item.r);
      if (achados.length >= LIMITE) break;
    }

    if (!achados.length) {
      contador.textContent = "Nenhuma rotina encontrada. Tente outra palavra (ex.: férias, carnê, ponto, certidão).";
      return;
    }
    contador.textContent = achados.length >= LIMITE
      ? "Mostrando as primeiras " + LIMITE + " rotinas encontradas — refine a busca para ver mais."
      : achados.length + (achados.length === 1 ? " rotina encontrada:" : " rotinas encontradas:");

    achados.forEach(function (r) {
      var li = el("li");
      var titulo = el("span", "r-titulo", r.t);
      titulo.appendChild(el("span", "r-mod", r.m));
      li.appendChild(titulo);
      if (r.c) li.appendChild(el("div", "r-caminho", r.c));
      if (r.d) li.appendChild(el("div", "r-desc", r.d));
      listaEl.appendChild(li);
    });
  }

  campo.addEventListener("input", buscar);
  filtro.addEventListener("change", buscar);
  buscar();
})();
